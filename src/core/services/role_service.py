

import logging

from src.core.enums.permission import RoleType
from src.core.models.role import Role, RolePermission
from src.present.dto.role.role import (
    CreateRoleDTO,
    GetRoleResponseDTO,
    Permission,
    RolePaginationResponse,
    UpdateRoleDTO,
)
from src.repository.role import RoleRepository

logger = logging.getLogger(__name__)


class RoleService:
    def __init__(self, role_repository: RoleRepository):
        self.role_repository = role_repository

    def get_org_roles(self, page: int, page_size: int):
        roles = self.role_repository.get_all(page, page_size)
        total = self.role_repository.count_total_roles(RoleType.ORGANIZATION)
        roles_dto = []
        for role in roles:
            perms = self.role_repository.get_role_permissions(role.id)
            perms_dto = [Permission(object=rp.object, action=rp.action) for rp in perms]
            roles_dto.append(
                GetRoleResponseDTO(id=role.id, name=role.name, permissions=perms_dto)
            )
        return RolePaginationResponse(
            roles=roles_dto,
            total=total,
            page=page,
            page_size=page_size,
        )

    def get_role_details(self, role_id: int):
        role = self.role_repository.get_by_id(role_id)
        perms = self.role_repository.get_role_permissions(role_id)
        perms_dto = [Permission(object=rp.object, action=rp.action) for rp in perms]
        return GetRoleResponseDTO(id=role.id, name=role.name, permissions=perms_dto)

    def create_org_role(self, create_role_dto: CreateRoleDTO):
        role = Role(
            role_type=RoleType.ORGANIZATION,
            name=create_role_dto.name,
        )
        role = self.role_repository.create_role(role)
        role_permissions = [
            RolePermission(
                role_id=role.id,
                object=permission.object,
                action=permission.action,
            )
            for permission in create_role_dto.permissions
        ]
        role_permissions = self.role_repository.create_role_permissions(
            role_permissions
        )
        permissions_dto = [
            Permission(object=rp.object, action=rp.action) for rp in role_permissions
        ]

        return GetRoleResponseDTO(
            id=role.id,
            name=role.name,
            permissions=permissions_dto,
        )

    def update_role(self, role_id: int, update_role_dto: UpdateRoleDTO):
        role = self.role_repository.get_by_id(role_id)
        role.name = update_role_dto.name
        role_permissions = [
            RolePermission(
                role_id=role.id,
                object=permission.object,
                action=permission.action,
            )
            for permission in update_role_dto.permissions
        ]
        role_permissions = self.role_repository.create_role_permissions(
            role_permissions
        )
        permissions_dto = [
            Permission(object=rp.object, action=rp.action) for rp in role_permissions
        ]
        self.role_repository.update_role(role, role_permissions)
        return GetRoleResponseDTO(
            id=role.id,
            name=role.name,
            permissions=permissions_dto,
        )

    def delete_role(self, role_id: int):
        return self.role_repository.delete_org_role(role_id)
