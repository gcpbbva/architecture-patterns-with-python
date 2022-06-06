import abc
import model


class AbstractRepository(abc.ABC):
    @abc.abstractmethod
    def add(self, batch: model.Batch):
        raise NotImplementedError

    @abc.abstractmethod
    def get(self, reference) -> model.Batch:
        raise NotImplementedError


class SqlRepository(AbstractRepository):
    def __init__(self, session):
        self.session = session

    def get_order_line(self, orderid, sku):
        result = self.session.execute(
            "SELECT id FROM order_lines WHERE orderid=:orderid AND sku=:sku",
            dict(orderid=orderid, sku=sku),
        )
        return result.first()

    def insert_order_line(self, sku, qty, orderid):
        if not self.get_order_line(orderid, sku):
            self.session.execute(
                """
                INSERT INTO 'order_lines' (sku, qty, orderid)
                VALUES (:sku, :qty, :orderid)
                """,
                {
                    'sku': sku,
                    'qty': qty,
                    'orderid': orderid
                }
            )
        [[orderline_id]] = self.session.execute(
            "SELECT id FROM order_lines WHERE orderid=:orderid AND sku=:sku",
            dict(orderid=orderid, sku=sku),
        )
        return orderline_id

    def insert_allocation(self, orderline_id, batch_id):
        self.session.execute(
            """
            INSERT INTO 'allocations' (orderline_id, batch_id)
            VALUES (:orderline_id, :batch_id)
            """,
            {
                'orderline_id': orderline_id,
                'batch_id': batch_id
            }
        )

    def get_batch(self, batch_id):
        batches = self.session.execute(
            """
            SELECT id FROM batches 
            WHERE reference=:batch_id
            """,
            {
                'batch_id': batch_id
            }
        )
        return batches.first()

    def insert_batch(self, batch):
        recovered_batch = self.get_batch(batch.reference)
        if not recovered_batch:
            self.session.execute(
                """
                INSERT INTO 'batches' (reference, sku, _purchased_quantity, eta)
                VALUES (:batch_reference, :sku, :qty, :eta)
                """,
                {
                    'batch_reference': batch.reference,
                    'sku': batch.sku,
                    'qty': batch._purchased_quantity,
                    'eta': batch.eta
                }
            )
        else:
            self.session.execute(
                """
                REPLACE INTO 'batches' (id, reference, sku, _purchased_quantity, eta)
                VALUES (:batch_id, :batch_reference, :sku, :qty, :eta)
                """,
                {
                    'batch_id': recovered_batch[0],
                    'batch_reference': batch.reference,
                    'sku': batch.sku,
                    'qty': batch._purchased_quantity,
                    'eta': batch.eta
                }
            )
        return self.get_batch(batch.reference)

    def add(self, batch):
        # self.session.execute('INSERT INTO ??
        inserted_batch = self.insert_batch(batch)
        for allocated_order_line in batch._allocations:
            orderline_id = self.insert_order_line(
                sku=allocated_order_line.sku,
                orderid=allocated_order_line.orderid,
                qty=allocated_order_line.qty
            )
            self.insert_allocation(
                orderline_id=orderline_id,
                batch_id=inserted_batch[0]
            )

    def get(self, reference) -> model.Batch:
        # self.session.execute('SELECT ??
        batches_recovered = self.session.execute(
            """
            SELECT * FROM batches
            where reference = :reference
            """,
            {
                'reference': reference
            }
        )
        first_element = batches_recovered.first()
        batch = model.Batch(*first_element[1:])

        order_lines = self.session.execute(
            """
            SELECT order_lines.orderid,
            order_lines.sku,
            order_lines.qty
            FROM allocations, order_lines
            where allocations.batch_id = :batch_id
            AND order_lines.id = allocations.orderline_id
            """,
            {
                'batch_id': first_element[0]
            }
        )
        for order_line in order_lines:
            batch.allocate(model.OrderLine(*order_line))
        return batch
