
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
        .when("/dashboard",{
            templateUrl: "views/dashboard.html",
            controller: "DashboardController"
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
                localStorage.setItem("access_token", response.data.access_token);
                console.log(response.data);
                $location.path("/dashboard");
            })
            .catch(function(error) {
                $scope.message = "Error: " + error.data.detail;
            });
    };
});

app.controller("DashboardController", function($scope, $http, $location) {
    var token = localStorage.getItem("access_token");

    // Redirect to login if no token
    if (!token) {
        $location.path("/login");
        return;
    }

    // Verify token with backend
    $http.get("http://127.0.0.1:8000/auth/verify", {
        headers: { "Authorization": "Bearer " + token }
    }).then(function(response) {
        $scope.user = response.data;  // Store user data
    }).catch(function(error) {
        console.error("Token verification failed:", error);
        localStorage.removeItem("access_token");  // Remove invalid token
        $location.path("/login");  // Redirect to login
    });

    // Logout function
    $scope.logoutUser = function() {
        localStorage.removeItem("access_token");
        $location.path("/login"); // Redirect to login page
    };
});


