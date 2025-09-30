from enum import Enum

OrgRoleDefault = "Default"
OrgRoleAdmin = "Admin"


class RoleType(str, Enum):
    ORGANIZATION = "Organization"
    PROJECT = "Project"


class Object(str, Enum):
    EMPLOYEE = "employee"
    PROJECT = "project"


class Action(str, Enum):
    READ = "read"
    CREATE = "create"
    UPDATE = "update"
    DELETE = "delete"
    DETAIL = "detail"


AllPermissions = {
    Object.EMPLOYEE: [
        Action.READ,
        Action.CREATE,
        Action.UPDATE,
        Action.DELETE,
        Action.DETAIL,
    ],
    Object.PROJECT: [
        Action.READ,
        Action.CREATE,
        Action.UPDATE,
        Action.DELETE,
    ],
}
