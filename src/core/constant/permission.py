from enum import Enum


class Object(str, Enum):
    EMPLOYEE = "employee"
    PROJECT = "project"


class Action(str, Enum):
    READ = "read"
    CREATE = "create"
    UPDATE = "update"
    DELETE = "delete"
    DETAIL = "detail"


Permission = {
    Object.EMPLOYEE: [
        Action.READ,
        Action.CREATE,
        Action.UPDATE,
        Action.DELETE,
    ],
    Object.PROJECT: [
        Action.READ,
        Action.CREATE,
        Action.UPDATE,
        Action.DELETE,
    ],
}
