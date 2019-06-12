import { shallowMount } from '@vue/test-utils'
import { NO_ACCESS, EditEnvironmentRole } from '../forms/edit_environment_role'

describe('EditEnvironmentRole', () => {
  var initialRoleCategories, wrapper

  beforeEach(() => {
    initialRoleCategories = [
      {
        role: NO_ACCESS,
        members: [
          { role_name: null, application_role_id: '123' },
          { role_name: null, application_role_id: '456' },
        ],
      },
      {
        role: 'Basic Access',
        members: [{ role_name: 'Basic Access', application_role_id: '789' }],
      },
      {
        role: 'Network Admin',
        members: [],
      },
      {
        role: 'Business Read-only',
        members: [
          { role_name: 'Business Read-only', application_role_id: '012' },
          { role_name: 'Business Read-only', application_role_id: '345' },
        ],
      },
      {
        role: 'Technical Read-only',
        members: [
          { role_name: 'Technical Read-only', application_role_id: '678' },
        ],
      },
    ]

    wrapper = shallowMount(EditEnvironmentRole, {
      propsData: { initialRoleCategories },
    })
  })

  it('removes null roles to no_access', () => {
    let roles = wrapper.vm.sanitizeValues([
      { role: NO_ACCESS, members: [{ role_name: null }] },
    ])
    expect(roles).toEqual([
      { role: NO_ACCESS, members: [{ role_name: NO_ACCESS }] },
    ])
  })

  it('gets the data for a user', () => {
    let member_data = wrapper.vm.getUserInfo('678')

    expect(member_data).toEqual({
      role_name: 'Technical Read-only',
      application_role_id: '678',
    })
  })

  it('removes a user from role', () => {
    let techRole = wrapper.vm.roleCategories.find(role => {
      return role.role === 'Technical Read-only'
    })

    expect(techRole.members.length).toEqual(1)
    wrapper.vm.removeUser('678')
    expect(techRole.members.length).toEqual(0)
  })

  it('adds user to a role', () => {
    let techRole = wrapper.vm.roleCategories.find(role => {
      return role.role === 'Technical Read-only'
    })

    expect(techRole.members.length).toEqual(1)
    wrapper.vm.addUser({ application_role_id: '901' }, 'Technical Read-only')
    expect(techRole.members.length).toEqual(2)
  })

  it('updates users role', () => {
    let techRole = wrapper.vm.roleCategories.find(role => {
      return role.role === 'Technical Read-only'
    })
    let businessRole = wrapper.vm.roleCategories.find(role => {
      return role.role === 'Business Read-only'
    })

    expect(techRole.members.length).toEqual(1)
    expect(businessRole.members.length).toEqual(2)
    wrapper.vm.updateRoles('678', 'Business Read-only')
    expect(techRole.members.length).toEqual(0)
    expect(businessRole.members.length).toEqual(3)
  })
})