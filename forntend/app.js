
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


});

app.controller("KnowledgeBaseController", function($scope, $http, FileUploadService, $location) {
    var token = localStorage.getItem("access_token");
    if (!token) {
        $scope.userFiles = [];
        $location.path("/login");
        return;
    }

    $scope.uploadMessage = "";
    $scope.userFiles = [];

    // Fetch user's uploaded files (if needed)
    $http.get("http://127.0.0.1:8000/files/myfiles", {
        headers: { "Authorization": "Bearer " + token }
    }).then(function(response) {
        $scope.userFiles = response.data;
        console.log("User files:", $scope.userFiles);
    }).catch(function(error) {
        console.error("Failed to fetch files:", error);
        $scope.userFiles = [];
    });

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
                // Optionally refresh the file list here
            })
            .catch(function(error) {
                console.error("File upload failed:", error);
                $scope.uploadMessage = "Upload failed. Try again.";
            });
    };
});

app.controller("ChatsController", function ($scope, $http) {
    $scope.chatHistory = [];  // Initialize chat history
    $scope.userMessage = "";  // Input field binding

    var token = localStorage.getItem("access_token");

    // Send message function
    $scope.sendMessage = function () {
        if (!$scope.userMessage.trim()) return;  // Prevent empty messages

        var data = { user_message: $scope.userMessage };

        $http.post("http://127.0.0.1:8000/chat/chat", data, {
            headers: { 
                "Authorization": "Bearer " + token,
                "Content-Type": "application/json"  // Ensure JSON request
            }
        }).then(function (response) {
            console.log("API Response:", response.data);

            $scope.$applyAsync(() => {
                // Push user message and Gemini response
                $scope.chatHistory.push({
                    user_message: $scope.userMessage,
                    gemini_response: response.data.gemini_response  // Adjust based on API response
                });
                $scope.userMessage = "";  // Clear input field
            });
        }).catch(function (error) {
            console.error("Chat API Error:", error);

            // Display error in chat history
            $scope.$applyAsync(() => {
                $scope.chatHistory.push({
                    user_message: $scope.userMessage,
                    gemini_response: "⚠️ Error: Unable to process request."
                });
            });
        });
    };
});

app.directive("fileModel", function($parse) {
    return {
        restrict: "A",
        link: function(scope, element, attrs) {
            var model = $parse(attrs.fileModel);
            var modelSetter = model.assign;
            element.bind("change", function(){
                scope.$apply(function(){
                    var selectedFile = element[0].files[0];
                    console.log("File selected:", selectedFile);  // This should log the file object
                    modelSetter(scope, selectedFile);
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



