# lib/review.py
from __init__ import CURSOR, CONN

class Review:

    # Dictionary to cache Review instances by their database ID
    all = {}

    def __init__(self, year, summary, employee_id, id=None):
        self.id = id
        self.year = year  # Triggers validation in the setter
        self.summary = summary
        self.employee_id = employee_id

    def __repr__(self):
        return (
            f"<Review {self.id}: {self.year}, {self.summary}, "
            + f"Employee: {self.employee_id}>"
        )#
    
    
    @property
    def employee_id(self):
        return self._employee_id

    @employee_id.setter
    def employee_id(self, value):
        from employee import Employee  # Avoid circular import
        if Employee.find_by_id(value) is not None:
            self._employee_id = value
        else:
            raise ValueError("Employee ID must reference an existing employee")

    @property
    def year(self):
        return self._year

    @year.setter
    def year(self, value):
        if isinstance(value, int) and value >= 2000:
            self._year = value
        else:
            raise ValueError("Year must be an integer greater than or equal to 2000")

    @property
    def summary(self):
        return self._summary

    @summary.setter
    def summary(self, value):
        if isinstance(value, str) and len(value) > 0:
            self._summary = value
        else:
            raise ValueError("Summary must be a non-empty string")
    

    @classmethod
    def create_table(cls):
        """ Create a new table to persist the attributes of Review instances """
        sql = """
            CREATE TABLE IF NOT EXISTS reviews (
                id INTEGER PRIMARY KEY,
                year INT,
                summary TEXT,
                employee_id INTEGER,
                FOREIGN KEY (employee_id) REFERENCES employees(id)
            )
        """
        CURSOR.execute(sql)
        CONN.commit()

    @classmethod
    def drop_table(cls):
        """ Drop the table that persists Review instances """
        sql = "DROP TABLE IF EXISTS reviews;"
        CURSOR.execute(sql)
        CONN.commit()

    def save(self):
        """
        Insert a new row with the year, summary, and employee_id of the Review object.
        Update the object's ID attribute with the primary key value from the new row.
        Store the object in the `all` dictionary using the row's primary key as the key.
        """
        if self.id is None:
            sql = """
                INSERT INTO reviews (year, summary, employee_id)
                VALUES (?, ?, ?)
            """
            CURSOR.execute(sql, (self.year, self.summary, self.employee_id))
            CONN.commit()
            self.id = CURSOR.lastrowid
            Review.all[self.id] = self
        else:
            self.update()

    # @classmethod
    # def create(cls, year, summary, employee_id):
    #     """ Initialize a new Review instance, save it to the database, and return the instance. """
    #     review = cls(year, summary, employee_id)
    #     review.save()
    #     return review

    # @classmethod
    # def instance_from_db(cls, row):
    #     """Return a Review instance created from a database row, using the cache if available."""
    #     review_id = row[0]

    #     # Check if the instance already exists in the cache
    #     if review_id in cls.all:
    #         review = cls.all[review_id]
    #         # Update attributes in case the database values changed
    #         review.year, review.summary, review.employee_id = row[1], row[2], row[3]
    #     else:
    #         # Create a new instance and cache it
    #         review = cls(row[1], row[2], row[3], id=row[0])
    #         cls.all[review_id] = review

    #     return review

    # @classmethod
    # def find_by_id(cls, id):
    #     """Return a Review instance corresponding to the specified primary key."""
    #     sql = "SELECT * FROM reviews WHERE id = ?"
    #     row = CURSOR.execute(sql, (id,)).fetchone()
    #     return cls.instance_from_db(row) if row else None

    def update(self):
        """Update the table row corresponding to the current Review instance."""
        sql = """
            UPDATE reviews
            SET year = ?, summary = ?, employee_id = ?
            WHERE id = ?
        """
        CURSOR.execute(sql, (self.year, self.summary, self.employee_id, self.id))
        CONN.commit()

    def delete(self):
        """Delete the table row for the current Review instance, remove it from the cache, and reset its ID."""
        sql = "DELETE FROM reviews WHERE id = ?"
        CURSOR.execute(sql, (self.id,))
        CONN.commit()
        if self.id in Review.all:
            del Review.all[self.id]
        self.id = None

    @classmethod
    def get_all(cls):
        """Return a list of all Review instances in the database."""
        sql = "SELECT * FROM reviews"
        rows = CURSOR.execute(sql).fetchall()
        return [cls.instance_from_db(row) for row in rows]
    
    @classmethod
    def find_by_employee_id(cls, employee_id):
        """Return a list of Review instances associated with a specific employee_id."""
        sql = """
            SELECT * FROM reviews WHERE employee_id = ?
        """
        rows = CURSOR.execute(sql, (employee_id,)).fetchall()
        return [cls.instance_from_db(row) for row in rows]
    
    # def save(self):
    #     """Insert or update a Review instance in the database."""
    #     if self.id is None:
    #         sql = """
    #             INSERT INTO reviews (year, summary, employee_id)
    #             VALUES (?, ?, ?)
    #         """
    #         CURSOR.execute(sql, (self.year, self.summary, self.employee_id))
    #         CONN.commit()
    #         self.id = CURSOR.lastrowid  # Capture the database ID
    #         Review.all[self.id] = self  # Cache the instance
    #     else:
    #         self.update()

    @classmethod
    def create(cls, year, summary, employee_id):
        """Create and persist a new Review instance."""
        review = cls(year, summary, employee_id)
        review.save()
        return review
    
    @classmethod
    def instance_from_db(cls, row):
        """Create or retrieve a Review instance from a database row."""
        if row[0] in cls.all:
            review = cls.all[row[0]]
            review.year, review.summary, review.employee_id = row[1], row[2], row[3]
        else:
            review = cls(row[1], row[2], row[3], id=row[0])
            cls.all[review.id] = review
        return review

    @classmethod
    def find_by_id(cls, id):
        """Retrieve a Review instance by ID."""
        sql = "SELECT * FROM reviews WHERE id = ?"
        row = CURSOR.execute(sql, (id,)).fetchone()
        return cls.instance_from_db(row) if row else None
