angular.module('hosts')

.factory('Host', ($http, Model) ->
    class Host extends Model
        @field 'id', defaults: null
        @field 'address', default: null
        @field 'port', default: 22

        url: ->
            if @id
                return "/api/v1/hosts/#{id}/"
            else
                return "/api/v1/hosts/"
    return Host
)