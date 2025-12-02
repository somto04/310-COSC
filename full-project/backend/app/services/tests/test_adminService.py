import pytest
from app.services import adminService
from app.schemas.user import User, CurrentUser, AdminUserUpdate
from app.schemas.role import Role


def makeUser(userId=1, role=Role.USER):
    return User(
        id=userId,
        username="user",
        firstName="First",
        lastName="Last",
        age=None,
        email="user@example.com",
        pw="hashed",
        role=role,
        penalties=0,
        isBanned=False,
        watchlist=[],
    )


def makeCurrentAdmin(adminId=1):
    return CurrentUser(
        id=adminId,
        username="admin",
        role=Role.ADMIN,
    )


def testGrantAdminCallsUpdateUserWithAdminRole(mocker):
    userId = 2
    currentAdmin = makeCurrentAdmin()
    updatedUser = makeUser(userId=userId, role=Role.ADMIN)

    updateUserMock = mocker.patch(
        "app.services.adminService.updateUser",
        return_value=updatedUser,
    )
    getUserByIdMock = mocker.patch(
        "app.services.adminService.getUserById",
        return_value=makeUser(userId=userId, role=Role.USER),
    )

    result = adminService.grantAdmin(userId, currentAdmin)

    getUserByIdMock.assert_called_once_with(userId)
    updateUserMock.assert_called_once_with(
        userId, AdminUserUpdate(role=Role.ADMIN)
    )
    assert result == updatedUser
    assert result.role == Role.ADMIN


def testGrantAdminRaisesAdminActionErrorWhenTargetIsCurrentAdmin():
    currentAdmin = makeCurrentAdmin()
    with pytest.raises(adminService.AdminActionError):
        adminService.grantAdmin(currentAdmin.id, currentAdmin)


def testGrantAdminRaisesAdminActionErrorWhenTargetIsAlreadyAdmin(mocker):
    userId = 2
    currentAdmin = makeCurrentAdmin()
    targetUser = makeUser(userId=userId, role=Role.ADMIN)

    mocker.patch(
        "app.services.adminService.getUserById",
        return_value=targetUser,
    )

    with pytest.raises(adminService.AdminActionError):
        adminService.grantAdmin(userId, currentAdmin)


def testRevokeAdminRaisesAdminActionErrorWhenTargetIsCurrentAdmin():
    currentAdmin = makeCurrentAdmin()
    with pytest.raises(adminService.AdminActionError):
        adminService.revokeAdmin(currentAdmin.id, currentAdmin)


def testRevokeAdminRaisesAdminActionErrorWhenTargetIsNotAdmin(mocker):
    userId = 2
    currentAdmin = makeCurrentAdmin()
    targetUser = makeUser(userId=userId, role=Role.USER)

    mocker.patch(
        "app.services.adminService.getUserById",
        return_value=targetUser,
    )

    with pytest.raises(adminService.AdminActionError):
        adminService.revokeAdmin(userId, currentAdmin)

def testRevokeAdminCallsUpdateUserWithUserRole(mocker):
    userId = 2
    currentAdmin = makeCurrentAdmin()
    updatedUser = makeUser(userId=userId, role=Role.USER)

    updateUserMock = mocker.patch(
        "app.services.adminService.updateUser",
        return_value=updatedUser,
    )
    getUserByIdMock = mocker.patch(
        "app.services.adminService.getUserById",
        return_value=makeUser(userId=userId, role=Role.ADMIN),
    )

    result = adminService.revokeAdmin(userId, currentAdmin)

    getUserByIdMock.assert_called_once_with(userId)
    updateUserMock.assert_called_once_with(
        userId, AdminUserUpdate(role=Role.USER)
    )
    assert result == updatedUser
    assert result.role == Role.USER
