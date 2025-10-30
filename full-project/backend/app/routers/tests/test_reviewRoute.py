"""
Integration Tests for Review Router

This file contains integration tests for the review API endpoints.
"""

import pytest
"""
Integration Tests for Review Router

This file contains integration tests for the review API endpoints.
"""

import pytest
from fastapi.testclient import TestClient
from app.routers.reviewRoute import getReview, postReview, getReviews, putReview, removeReview
from app.services.reviewService import ReviewCreate
from app.app import app
from app.routers.auth import requireAdmin

# mock user for testing overriding the authentication file requiring an admin
app.dependency_overrides[requireAdmin] = lambda: {"username": "testuser", "role": "admin"}

# temporary mock for testing
#def getCurrentUser():
#    return {"username": "testuser", "role": "admin"}

client = TestClient(app)

def test_getReviews():
    response = client.get("/reviews")  
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_postReview():
    payload = {
        "movieId": 1,
        "userId": 1,
        "username": "testuser",
        "reviewTitle": "Great Movie!",
        "reviewBody": "This movie was amazing, highly recommend",
        "rating": "5",
        "username": "testuser",
        "reviewTitle": "Great Movie!",
        "reviewBody": "This movie was amazing, highly recommend",
        "rating": "5",
        "flagged": False
    }

# sample list of reviews for testing
@pytest.fixture
def sample_reviews_list(sample_review_data):
    """Sample list of reviews for testing"""
    return [
        sample_review_data,
        {
            "id": "2",
            "movieId": 1,
            "userId": 2,
            "username": "anotheruser",
            "reviewTitle": "Not bad",
            "reviewBody": "It was okay, nothing special",
            "rating": "3",
            "flagged": False
        },
        {
            "id": "3",
            "movieId": 2,
            "userId": 1,
            "username": "testuser",
            "reviewTitle": "Disappointed",
            "reviewBody": "Expected better from this film",
            "rating": "2",
            "flagged": False
        }
    ]


# ============================================================================
# INTEGRATION TESTS - Testing API endpoints with HTTP requests
# ============================================================================

class TestReviewRouterIntegration:
    """Integration tests for review API endpoints"""
    
    @patch('app.routers.reviewRoute.listReviews')
    def test_get_all_reviews_endpoint(self, mock_list, client, sample_reviews_list):
        """Test GET /reviews returns all reviews"""
        # Arrange
        mock_list.return_value = sample_reviews_list
        
        # Act
        response = client.get("/reviews")
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 3
        assert data[0]["reviewTitle"] == "Great Movie!"
        assert data[1]["reviewTitle"] == "Not bad"
    
    
    @patch('app.routers.reviewRoute.getReviewById')
    def test_get_review_by_id_endpoint(self, mock_get, client, sample_review_data):
        """Test GET /reviews/{id} returns specific review"""
        # Arrange
        mock_get.return_value = sample_review_data
        
        # Act
        response = client.get("/reviews/1")
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == "1"
        assert data["reviewTitle"] == "Great Movie!"
        assert data["rating"] == "5"
        mock_get.assert_called_once_with("1")
    
    
    @patch('app.routers.reviewRoute.getReviewById')
    def test_get_review_by_id_not_found(self, mock_get, client):
        """Test GET /reviews/{id} with non-existent ID returns 404"""
        # Arrange
        mock_get.side_effect = HTTPException(status_code=404, detail="Review not found")
        
        # Act
        response = client.get("/reviews/999")
        
        # Assert
        assert response.status_code == 404
        assert response.json()["detail"] == "Review not found"
    
    
    @patch('app.routers.reviewRoute.searchReviews')
    def test_search_reviews_with_query(self, mock_search, client, sample_review_data):
        """Test GET /reviews/search?q=keyword returns matching reviews"""
        # Arrange
        mock_search.return_value = [sample_review_data]
        
        # Act
        response = client.get("/reviews/search?q=great")
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["reviewTitle"] == "Great Movie!"
        mock_search.assert_called_once_with("great")
    
    
    @patch('app.routers.reviewRoute.searchReviews')
    def test_search_reviews_with_limit_and_offset(self, mock_search, client, sample_reviews_list):
        """Test search with limit and offset parameters"""
        # Arrange
        mock_search.return_value = sample_reviews_list
        
        # Act
        response = client.get("/reviews/search?q=movie&limit=2&offset=1")
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2  # Limited to 2 results
        assert data[0]["id"] == "2"  # Starting from offset 1
    
    
    @patch('app.routers.reviewRoute.createReview')
    def test_create_review_endpoint(self, mock_create, client, sample_review_data):
        """Test POST /reviews creates a new review"""
        # Arrange
        mock_create.return_value = sample_review_data
        
        new_review = {
            "movieId": 1,
            "userId": 1,
            "reviewTitle": "Great Movie!",
            "reviewBody": "This movie was amazing, highly recommend",
            "rating": "5"
        }
        
        # Act
        response = client.post("/reviews", json=new_review)
        
        # Assert
        assert response.status_code == 201
        data = response.json()
        assert data["reviewTitle"] == "Great Movie!"
        assert data["rating"] == "5"
    
    
    @patch('app.routers.reviewRoute.updateReview')
    def test_update_review_endpoint(self, mock_update, client, sample_review_data):
        """Test PUT /reviews/{id} updates a review.
        It verifies that the FastAPI route for updating a review correctly
        updates an existing review's data and returns the modified view. 
        """
        # Arrange
        updated_review = sample_review_data.copy()
        updated_review["reviewBody"] = "Updated review text"
        updated_review["rating"] = "4"
        mock_update.return_value = updated_review
        
        update_data = {
            "reviewBody": "Updated review text",
            "rating": "4"
        }
        
        # Act
        response = client.put("/reviews/1", json=update_data)
        
        # Assert
        assert response.status_code == 200
# sample list of reviews for testing
@pytest.fixture
def sample_reviews_list(sample_review_data):
    """Sample list of reviews for testing"""
    return [
        sample_review_data,
        {
            "id": "2",
            "movieId": 1,
            "userId": 2,
            "username": "anotheruser",
            "reviewTitle": "Not bad",
            "reviewBody": "It was okay, nothing special",
            "rating": "3",
            "flagged": False
        },
        {
            "id": "3",
            "movieId": 2,
            "userId": 1,
            "username": "testuser",
            "reviewTitle": "Disappointed",
            "reviewBody": "Expected better from this film",
            "rating": "2",
            "flagged": False
        }
    ]


# ============================================================================
# INTEGRATION TESTS - Testing API endpoints with HTTP requests
# ============================================================================

class TestReviewRouterIntegration:
    """Integration tests for review API endpoints"""
    
    @patch('app.routers.reviewRoute.listReviews')
    def test_get_all_reviews_endpoint(self, mock_list, client, sample_reviews_list):
        """Test GET /reviews returns all reviews"""
        # Arrange
        mock_list.return_value = sample_reviews_list
        
        # Act
        response = client.get("/reviews")
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 3
        assert data[0]["reviewTitle"] == "Great Movie!"
        assert data[1]["reviewTitle"] == "Not bad"
    
    
    @patch('app.routers.reviewRoute.getReviewById')
    def test_get_review_by_id_endpoint(self, mock_get, client, sample_review_data):
        """Test GET /reviews/{id} returns specific review"""
        # Arrange
        mock_get.return_value = sample_review_data
        
        # Act
        response = client.get("/reviews/1")
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == "1"
        assert data["reviewTitle"] == "Great Movie!"
        assert data["rating"] == "5"
        mock_get.assert_called_once_with("1")
    
    
    @patch('app.routers.reviewRoute.getReviewById')
    def test_get_review_by_id_not_found(self, mock_get, client):
        """Test GET /reviews/{id} with non-existent ID returns 404"""
        # Arrange
        mock_get.side_effect = HTTPException(status_code=404, detail="Review not found")
        
        # Act
        response = client.get("/reviews/999")
        
        # Assert
        assert response.status_code == 404
        assert response.json()["detail"] == "Review not found"
    
    
    @patch('app.routers.reviewRoute.searchReviews')
    def test_search_reviews_with_query(self, mock_search, client, sample_review_data):
        """Test GET /reviews/search?q=keyword returns matching reviews"""
        # Arrange
        mock_search.return_value = [sample_review_data]
        
        # Act
        response = client.get("/reviews/search?q=great")
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["reviewTitle"] == "Great Movie!"
        mock_search.assert_called_once_with("great")
    
    
    @patch('app.routers.reviewRoute.searchReviews')
    def test_search_reviews_with_limit_and_offset(self, mock_search, client, sample_reviews_list):
        """Test search with limit and offset parameters"""
        # Arrange
        mock_search.return_value = sample_reviews_list
        
        # Act
        response = client.get("/reviews/search?q=movie&limit=2&offset=1")
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2  # Limited to 2 results
        assert data[0]["id"] == "2"  # Starting from offset 1
    
    
    @patch('app.routers.reviewRoute.createReview')
    def test_create_review_endpoint(self, mock_create, client, sample_review_data):
        """Test POST /reviews creates a new review"""
        # Arrange
        mock_create.return_value = sample_review_data
        
        new_review = {
            "movieId": 1,
            "userId": 1,
            "reviewTitle": "Great Movie!",
            "reviewBody": "This movie was amazing, highly recommend",
            "rating": "5"
        }
        
        # Act
        response = client.post("/reviews", json=new_review)
        
        # Assert
        assert response.status_code == 201
        data = response.json()
        assert data["reviewTitle"] == "Great Movie!"
        assert data["rating"] == "5"
    
    
    @patch('app.routers.reviewRoute.updateReview')
    def test_update_review_endpoint(self, mock_update, client, sample_review_data):
        """Test PUT /reviews/{id} updates a review.
        It verifies that the FastAPI route for updating a review correctly
        updates an existing review's data and returns the modified view. 
        """
        # Arrange
        updated_review = sample_review_data.copy()
        updated_review["reviewBody"] = "Updated review text"
        updated_review["rating"] = "4"
        mock_update.return_value = updated_review
        
        update_data = {
            "reviewBody": "Updated review text",
            "rating": "4"
        }
        
        # Act
        response = client.put("/reviews/1", json=update_data)
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["reviewBody"] == "Updated review text"
        assert data["rating"] == "4"
    
    
    @patch('app.routers.reviewRoute.deleteReview')
    @patch('app.routers.reviewRoute.getReviewById')
    def test_delete_review_as_admin(self, mock_get_review, mock_delete, client, sample_review_data, app):
        """Test DELETE /reviews/{id} as admin"""
        # Override getCurrentUser dependency
        app.dependency_overrides[getCurrentUser] = lambda: {"username": "admin", "role": "admin"}

        # Arrange
        mock_get_review.return_value = sample_review_data
        mock_delete.return_value = None

        # Act
        response = client.delete("/reviews/1")

        # Assert
        assert response.status_code == status.HTTP_204_NO_CONTENT
        mock_delete.assert_called_once_with("1")

        # Cleanup
        app.dependency_overrides = {}
    
    
    @patch('app.routers.reviewRoute.getReviewById')
    def test_delete_review_not_found(self, mock_get_review, client, app):
        """Test DELETE /reviews/{id} when review doesn't exist"""
        # Override getCurrentUser dependency
        app.dependency_overrides[getCurrentUser] = lambda: {"username": "admin", "role": "admin"}

        # Arrange
        mock_get_review.return_value = None

        # Act
        response = client.delete("/reviews/999")

        # Assert
        assert response.status_code == 404
        assert response.json()["detail"] == "Review not found"

        # Cleanup
        app.dependency_overrides = {}


# ============================================================================
# HOW TO RUN THESE TESTS
# ============================================================================
"""
To run all tests:
    pytest app/routers/tests/test_reviewRoute.py -v

To run only integration tests:
    pytest app/routers/tests/test_reviewRoute.py::TestReviewRouterIntegration -v

To run a specific test:
    pytest app/routers/tests/test_reviewRoute.py::TestReviewRouterIntegration::test_get_all_reviews_endpoint -v

To see print statements:
    pytest app/routers/tests/test_reviewRoute.py -v -s
"""
        assert data["reviewBody"] == "Updated review text"
        assert data["rating"] == "4"
    
    
    @patch('app.routers.reviewRoute.deleteReview')
    @patch('app.routers.reviewRoute.getReviewById')
    def test_delete_review_as_admin(self, mock_get_review, mock_delete, client, sample_review_data, app):
        """Test DELETE /reviews/{id} as admin"""
        # Override getCurrentUser dependency
        app.dependency_overrides[getCurrentUser] = lambda: {"username": "admin", "role": "admin"}

        # Arrange
        mock_get_review.return_value = sample_review_data
        mock_delete.return_value = None

        # Act
        response = client.delete("/reviews/1")

        # Assert
        assert response.status_code == status.HTTP_204_NO_CONTENT
        mock_delete.assert_called_once_with("1")

        # Cleanup
        app.dependency_overrides = {}
    
    
    @patch('app.routers.reviewRoute.getReviewById')
    def test_delete_review_not_found(self, mock_get_review, client, app):
        """Test DELETE /reviews/{id} when review doesn't exist"""
        # Override getCurrentUser dependency
        app.dependency_overrides[getCurrentUser] = lambda: {"username": "admin", "role": "admin"}

        # Arrange
        mock_get_review.return_value = None

        # Act
        response = client.delete("/reviews/999")

        # Assert
        assert response.status_code == 404
        assert response.json()["detail"] == "Review not found"

        # Cleanup
        app.dependency_overrides = {}


# ============================================================================
# HOW TO RUN THESE TESTS
# ============================================================================
"""
To run all tests:
    pytest app/routers/tests/test_reviewRoute.py -v

To run only integration tests:
    pytest app/routers/tests/test_reviewRoute.py::TestReviewRouterIntegration -v

To run a specific test:
    pytest app/routers/tests/test_reviewRoute.py::TestReviewRouterIntegration::test_get_all_reviews_endpoint -v

To see print statements:
    pytest app/routers/tests/test_reviewRoute.py -v -s
"""
