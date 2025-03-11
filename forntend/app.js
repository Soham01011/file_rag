
var app = angular.module("myApp", ["ngRoute"]);

app.config(function($routeProvider) {
    $routeProvider
        .when("/", {
            templateUrl: "views/home.html"
        })
        .when("/register", {
            templateUrl: "views/register.html",
            controller: "RegisterController"
        })
        .when("/login", {
            templateUrl: "views/login.html",
            controller: "LoginController"
        })
        .otherwise({
            redirectTo: "/"
        });
});

app.controller("RegisterController", function($scope, $http) {
  $scope.user = {};
  $scope.message = "";

  $scope.registerUser = function() {
      console.log("User Data Submitted:", $scope.user);

      $http.post("http://127.0.0.1:8000/auth/register", $scope.user)
          .then(function(response) {
              console.log("Response from API:", response.data);
              
              // Store the received token (optional, for login persistence)
              localStorage.setItem("access_token", response.data.access_token);

              $scope.message = "Registration successful! Token stored.";
          })
          .catch(function(error) {
              console.error("Error from API:", error);
              $scope.message = "Error: " + (error.data.detail || "Registration failed");
          });
  };
});

app.controller("LoginController", function($scope, $http) {
    $scope.user = {};
    $scope.message = "";

    $scope.loginUser = function() {
        $http.post("http://127.0.0.1:8000/auth/login", $scope.user)
            .then(function(response) {
                $scope.message = "Login successful! ", JSON.stringify(response.data);
                console.log(response.data);
            })
            .catch(function(error) {
                $scope.message = "Error: " + error.data.detail;
            });
    };
});
