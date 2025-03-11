// Define the AngularJS module
angular.module('myApp', [])
  
  // Service to handle API calls for authentication
  .service('AuthService', function($http) {
    // Adjust the URL to match your FastAPI backend
    const API_URL = 'http://localhost:8000/auth/login';
    
    this.login = function(user) {
      return $http.post(API_URL, user);
    };
  })
  
  // Controller for the login form
  .controller('AuthController', function($scope, AuthService) {
    $scope.user = {};
    $scope.errorMessage = '';
    
    $scope.login = function() {
      AuthService.login($scope.user)
        .then(function(response) {
          // Handle successful login
          console.log("Login success:", response.data);
          $scope.errorMessage = '';
          // Save token (e.g., in localStorage for later use)
          localStorage.setItem('access_token', response.data.access_token);
          // Optionally redirect to another page or update UI
        })
        .catch(function(error) {
          // Handle login error
          console.error("Login failed:", error.data);
          $scope.errorMessage = error.data.detail || "Login failed. Please try again.";
        });
    };
  });
