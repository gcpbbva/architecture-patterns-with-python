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

    def insert_order_line(self, sku, qty, orderid):
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

    def get_batch(self, reference):
        [[batch_id]] = self.session.execute(
            'SELECT id FROM batches WHERE reference=:reference',
            dict(reference=reference),
        )
        return batch_id

    def insert_batch(self, batch):
        if self.get_batch(batch.reference):
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
            [[batch_id]] = self.session.execute(
                'SELECT id FROM batches WHERE reference=:reference',
                dict(reference=batch.reference),
            )
            return batch_id

    def add(self, batch):
        # self.session.execute('INSERT INTO ??
        batch_id = self.insert_batch(batch)
        for allocated_order_line in batch._allocations:
            orderline_id = self.insert_order_line(
                sku=allocated_order_line.sku,
                orderid=allocated_order_line.orderid,
                qty=allocated_order_line.qty
            )
            self.insert_allocation(
                orderline_id=orderline_id,
                batch_id=batch_id
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
