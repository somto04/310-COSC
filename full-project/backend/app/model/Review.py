class Review:
    ReviewID: int
    UserID: int
    title: str
    content: str
    rating: int

    def __init__(self, ReviewID: int, UserID: int, title: str, content: str, rating: int):
        self.ReviewID = ReviewID
        self.UserID = UserID
        self.title = title
        self.content = content
        self.rating = rating

    