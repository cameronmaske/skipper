angular.module('hosts')

.factory('Host', ($http, Model) ->
    class Host extends Model
        @field 'id', defaults: null
        @field 'host', default: null
        @field 'port', default: null
        @field 'ssh_setup', default: false

        url: ->
            if @id
                return "/api/v1/hosts/#{id}/"
            else
                return "/api/v1/hosts/"
    return Host
)