angular.module('common')

.factory('pleaseHold', ->
    loading = {
        state: false
        message: null
    }

    init: ->
        return loading

    start:  (message=null) ->
        loading.state = true
        loading.message = null

    finished: ->
        loading.state = false
        loading.message = null
)