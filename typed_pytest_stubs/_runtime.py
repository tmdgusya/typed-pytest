"""Runtime-accessible placeholder classes for stub package.



These classes are used at runtime when importing from typed_pytest_stubs.

"""

from __future__ import annotations



import typing



class UserService:
    def async_create_user(self, name: str, email: str) -> typing.Any: ...
    def async_get_user(self, user_id: int) -> typing.Any: ...
    def create_user(self, name: str, email: str) -> typing.Any: ...
    def delete_user(self, user_id: int) -> typing.Any: ...
    def from_config(config: dict[str, typing.Any]) -> typing.Any: ...
    def get_user(self, user_id: int) -> typing.Any: ...
    def update_user(self, user_id: int, *, name: str | None = None, email: str | None = None) -> typing.Any: ...
    def validate_email(email: str) -> typing.Any: ...

class UserService_TypedMock:
    pass
class UserServiceMock(UserService_TypedMock):
    pass

class ProductRepository:
    def find_all(self, limit: int = 10) -> typing.Any: ...
    def find_by_id(self, product_id: str) -> typing.Any: ...
    def search(self, query: str, *, max_results: int = 100) -> typing.Any: ...

class ProductRepository_TypedMock:
    pass
class ProductRepositoryMock(ProductRepository_TypedMock):
    pass

