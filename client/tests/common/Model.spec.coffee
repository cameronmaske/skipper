describe 'Model', ->
    # Globally defined.
    Model = null
    User = null

    beforeEach(angular.mock.module('common'))

    beforeEach(inject (_Model_) ->
        # This is the standard way to mock with Angular and inject
        # in various required functionality.
        Model = _Model_
        class User extends Model
            @field 'name', default: 'Jonathan'
            @field 'currentStatus', default: 'happy'
        @user = new User()
    )

    it 'should set and get fields', ->
        expect(@user.name).toEqual('Jonathan')
        @user.name = 'Cameron'
        expect(@user.name).toEqual('Cameron')
        newUser = new User({name: 'Fletcher'})
        expect(newUser.name).toEqual('Fletcher')

    it 'should output to a server format', ->
        expect(@user.toServer()).toEqual({
            'name': 'Jonathan'
            'current_status': 'happy'})

    it 'should parse from a server', ->
        response = {
            'name': 'Cameron'
            'current_status': 'sad'
        }

        newUser = new User()
        newUser.fromServer(response)
