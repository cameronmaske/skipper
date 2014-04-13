angular.module('common')

.factory('Oops', ->
    errors = {
        current: null
    }

    init: ->
        return errors

    clearError:  ->
        error.current = null

    setError: (message) ->
        error.current = message
)