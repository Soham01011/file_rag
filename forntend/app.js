
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

app.controller("DashboardController", function($scope, FileUploadService, $http, $location) {
    var token = localStorage.getItem("access_token");

    if (!token) {
        $location.path("/login");
        return;
    }

    // Default to 'chats' tab
    $scope.activeTab = "chats";  

    // Function to change tabs
    $scope.setTab = function(tabName) {
        $scope.activeTab = tabName;
    };

    // Verify token
    $http.get("http://127.0.0.1:8000/auth/verify", {
        headers: { "Authorization": "Bearer " + token }
    }).then(function(response) {
        $scope.$applyAsync(function() {
            $scope.username = response.data.sub;
        });
    }).catch(function(error) {
        console.error("Token verification failed:", error);
        localStorage.removeItem("access_token");
        $location.path("/login");
    });

    $scope.logoutUser = function() {
        localStorage.removeItem("access_token");
        $location.path("/login");
    };

    // Handle File Upload
    $scope.uploadFile = function() {
        if (!$scope.file) {
            $scope.uploadMessage = "Please select a file first.";
            return;
        }

        FileUploadService.uploadFile($scope.file)
            .then(function(response) {
                $scope.uploadMessage = "File uploaded successfully!";
                console.log("Upload response:", response);
            })
            .catch(function(error) {
                console.error("File upload failed:", error);
                $scope.uploadMessage = "Upload failed. Try again.";
            });
    };
});

// Directive to handle file input binding
app.directive("fileModel", function($parse) {
    return {
        restrict: "A",
        link: function(scope, element, attrs) {
            var model = $parse(attrs.fileModel);
            var modelSetter = model.assign;

            element.bind("change", function() {
                scope.$apply(function() {
                    modelSetter(scope, element[0].files[0]);
                });
            });
        }
    };
});

app.service("FileUploadService", function($http) {
    this.uploadFile = function(file) {
        var token = localStorage.getItem("access_token");
        if (!token) {
            return Promise.reject("No access token found.");
        }

        var formData = new FormData();
        formData.append("file", file);

        return $http.post("http://127.0.0.1:8000/files/upload", formData, {
            headers: {
                "Content-Type": undefined, // Let the browser set multipart/form-data
                "Authorization": "Bearer " + token
            }
        }).then(response => response.data)
          .catch(error => Promise.reject(error));
    };
});



