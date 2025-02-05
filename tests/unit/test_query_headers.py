from unittest import mock

from dbt.adapters.athena import _QueryComment
from dbt.adapters.base.query_headers import MacroQueryStringSetter

from .constants import AWS_REGION, DATA_CATALOG_NAME, DATABASE_NAME
from .utils import config_from_parts_or_dicts


class TestQueryHeaders:

    query_header = MacroQueryStringSetter(
        config_from_parts_or_dicts(
            {
                "name": "query_headers",
                "version": "0.1",
                "profile": "test",
                "config-version": 2,
            },
            {
                "outputs": {
                    "test": {
                        "type": "athena",
                        "s3_staging_dir": "s3://my-bucket/test-dbt/",
                        "region_name": AWS_REGION,
                        "database": DATA_CATALOG_NAME,
                        "work_group": "dbt-athena-adapter",
                        "schema": DATABASE_NAME,
                    }
                },
                "target": "test",
            },
        ),
        mock.MagicMock(macros={}),
    )
    query_header.comment = _QueryComment(None)

    def test_append_comment_with_semicolon(self):
        self.query_header.comment.query_comment = "executed by dbt"
        self.query_header.comment.append = True
        sql = self.query_header.add("SELECT 1;")
        assert sql == "SELECT 1\n-- /* executed by dbt */;"

    def test_append_comment_without_semicolon(self):
        self.query_header.comment.query_comment = "executed by dbt"
        self.query_header.comment.append = True
        sql = self.query_header.add("SELECT 1")
        assert sql == "SELECT 1\n-- /* executed by dbt */"

    def test_comment_multiple_lines(self):
        self.query_header.comment.query_comment = """executed by dbt\nfor table table"""
        self.query_header.comment.append = False
        sql = self.query_header.add("insert into table(id) values (1);")
        assert sql == "-- /* executed by dbt for table table */\ninsert into table(id) values (1);"

    def test_disable_query_comment(self):
        self.query_header.comment.query_comment = ""
        self.query_header.comment.append = True
        assert self.query_header.add("SELECT 1;") == "SELECT 1;"

    def test_no_query_comment_on_alter(self):
        self.query_header.comment.query_comment = "executed by dbt"
        self.query_header.comment.append = True
        sql = "alter table table add column time time;"
        assert self.query_header.add(sql) == sql

    def test_no_query_comment_on_vacuum(self):
        self.query_header.comment.query_comment = "executed by dbt"
        self.query_header.comment.append = True
        sql = "VACUUM table"
        assert self.query_header.add(sql) == sql
