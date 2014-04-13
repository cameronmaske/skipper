angular.module('common')

.factory('Model', ($q, $log, $http) ->
    camelCase = (input) ->
      input.toLowerCase().replace(/-(.)/g, (match, group) ->
        return group.toUpperCase())

    underScore = (input) ->
        input.replace(/([A-Z])/g, (match) ->
            return "_"+ match .toLowerCase())

    notImplementedException = (message) ->
        return message

    class Model
        ###
        A base model class that does most of the common heavy lifting!

        Example:

            class User extends Model
                @id 'id', defaults: null
                @field 'name', default: 'Jonathan'
                @field 'friends', defaults: -> []
                url: -> "/api/user/{@id}"

            >>> user = new User()
            >>> user.name
            'Jonathan'
            >>> user.friends.length
            0

        Note: When declaring a field that points to a javascript object (e.g
        {}, [], new Object()...) it's best to declare to be invoked by a function
        (e.g. the 'friends field above').
        Otherwise, all models made will share the same Object. This means that
        declaring a 'new Model' with not reset the field.
        ###
        @field: (name, options) ->
            # Allow you to declare fields easily on a Model class.
            # Coffeescript fun: The @ sign at the start means it's a static method.
            # Globally avaliable across all models (not object specific)
            @fields ?= {}
            @fields[name] = options or {}

        constructor: (attributes, kwargs={}) ->
            # Runs where a model is first initialized.
            # Based on the fields declare, takes the attributes and assigns them
            # to the model.

            # Record a list of all the field names (used in other functions)
            fieldNames = []
            # Copy in attributes passed in or defaults from the fields as appropriate
            for name, options of @constructor.fields
                # Assign value to the property of the object.
                value = attributes?[name]
                if _.isUndefined(attributes?[name])
                    value = if angular.isFunction(options.default) then options.default() else options.default
                @[name] = value
                # Add the field name to a list.
                fieldNames.push(name)
            @fieldNames = fieldNames

        toServer: ->
            attributes = {}
            for field in @fieldNames
                value = @[field]
                attributes(underScore(field)) = value
            return attributes

        fromServer: (attributes) ->
            for key, value of attributes
                camelKey = camelCase(key)
                if camelKey in @fieldNames
                    @[camelKey] = value

        url: ->
            throw new notImplementedException("url() function is not implemented.")

        save: ->
            deferred = $q.defer()

            $http({method: 'POST', url:@url(), data:@toServer()})
                .success (data) =>
                    @fromServer(data)
                    $log.info("Succesfully saved the #{@constructor.name}.")
                    deferred.resolve(data)
                .error (data) =>
                    $log.error("Failed to save the #{@constructor.name}..")
                    deferred.reject(data)

            return deferred.promise

        remove: ->
            deferred = $q.defer()

            $http({method:'DELETE', url:@url()})
                .success (data) ->
                    $log.info("Succesfully delete the #{@constructor.name}")
                    deferred.resolve(data)
                .error (data) ->
                    $log.error("Failed to delete the #{@constructor.name}")
                    deferred.reject(data)
            return deferred.promise
    return Model
)