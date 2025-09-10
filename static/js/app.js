function activeMenuOption(href) {
    $(".app-menu .nav-link")
    .removeClass("active")
    .removeAttr('aria-current')

    $(`[href="${(href ? href : "#/")}"]`)
    .addClass("active")
    .attr("aria-current", "page")
}

const app = angular.module("angularjsApp", ["ngRoute"])
app.config(function ($routeProvider, $locationProvider) {
    $locationProvider.hashPrefix("")

    $routeProvider
    .when("/", {
        templateUrl: "/app",
        controller: "appCtrl"
    })
    .when("/mascotas", {
        templateUrl: "/mascotas",
        controller: "mascotasCtrl"
    })
    .otherwise({
        redirectTo: "/"
    })
})
app.run(["$rootScope", "$location", "$timeout", function($rootScope, $location, $timeout) {
    function actualizarFechaHora() {
        lxFechaHora = DateTime
        .now()
        .setLocale("es")

        $rootScope.angularjsHora = lxFechaHora.toFormat("hh:mm:ss a")
        $timeout(actualizarFechaHora, 1000)
    }

    $rootScope.slide = ""

    actualizarFechaHora()

    $rootScope.$on("$routeChangeSuccess", function (event, current, previous) {
        $("html").css("overflow-x", "hidden")
        
        const path = current.$$route.originalPath

        if (path.indexOf("splash") == -1) {
            const active = $(".app-menu .nav-link.active").parent().index()
            const click  = $(`[href^="#${path}"]`).parent().index()

            if (active != click) {
                $rootScope.slide  = "animate__animated animate__faster animate__slideIn"
                $rootScope.slide += ((active > click) ? "Left" : "Right")
            }

            $timeout(function () {
                $("html").css("overflow-x", "auto")

                $rootScope.slide = ""
            }, 1000)

            activeMenuOption(`#${path}`)
        }
    })
}])

app.controller("appCtrl", function ($scope, $http) {
    $("#frmInicioSesion").submit(function (event) {
        event.preventDefault()
        $.post("iniciarSesion", $(this).serialize(), function (respuesta) {
            if (respuesta.length) {
                alert("Iniciaste Sesión")
                window.location = "/#/mascotas"

                return
            }

            alert("Usuario y/o Contraseña Incorrecto(s)")
        })
    })
})
app.controller("mascotasCtrl", function ($scope, $http) {
    function buscarMascotas() {
        $.get("/tbodyMascotas", function (trsHTML) {
            $("#tbodyMascotas").html(trsHTML)
        })
    }

    buscarMascotas()
    
    // Enable pusher logging - don't include this in production
    Pusher.logToConsole = true

    var pusher = new Pusher("c018d337fb7e8338dc3a", {
      cluster: "us2"
    })

    var channel = pusher.subscribe("rapid-bird-168")
    channel.bind("eventoMascotas", function(data) {
        // alert(JSON.stringify(data))
        buscarMascotas()
    })

    $(document).on("submit", "#frmMascota", function (event) {
        event.preventDefault()

        $.post("/mascota", {
            idMascota: "",
            nombre:      $("#txtNombre").val(),
            sexo:        $("#txtSexo").val(),
            raza:        $("#txtRaza").val(),
            peso:        $("#txtPeso").val(),
            condiciones: $("#txtCondiciones").val(),
        })
    })

    $(document).off("click", ".btn-eliminar").on("click", ".btn-eliminar", function () {
        const id = $(this).data("id")
    
        if (!confirm("¿Seguro que deseas eliminar esta mascota?")) {
            return
        }
    
        $.post("/mascota/eliminar", { idMascota: id }, function () {
            buscarMascotas()
        }).fail(function(xhr) {
            alert("Error al eliminar: " + xhr.responseText)
        })
    })
})

const DateTime = luxon.DateTime
let lxFechaHora

document.addEventListener("DOMContentLoaded", function (event) {
    const configFechaHora = {
        locale: "es",
        weekNumbers: true,
        // enableTime: true,
        minuteIncrement: 15,
        altInput: true,
        altFormat: "d/F/Y",
        dateFormat: "Y-m-d",
        // time_24hr: false
    }

    activeMenuOption(location.hash)
})


