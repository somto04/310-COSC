# SpoilerAlert - A Movie Reviewing Application
COSC-310 Project by CTRL-ALT-DEFEAT

## Description

SpoilerAlert! is a movie review platform built with FastAPI that lets users browse films, read and write reviews, and discover new recommendations. The system includes full user authentication, role-based permissions, movie filtering/search, and community-driven review interactions. It also integrates with the TMDb API to fetch real-time movie details and recommendations.

The backend manages all core logic including reviews, replies, penalties, user accounts, and movie data, while the frontend delivers a clean, responsive UI for both casual users and admins. The platform is designed to be modular, testable, and easy to extend.

## How to Run the Webpage

Before running the system, install the following tools:

Docker Desktop (version 4.x or newer)
https://www.docker.com/products/docker-desktop/

VSCode
https://code.visualstudio.com/

### Option 1 - Using VSCode Terminal:
1. Open the project in VSCode (clone from GitHub repo)
2. Make sure you are in the folder that contains `docker-compose.yml` (e.g., 310-COSC):

`cd 310-COSC`

3. Run the containers in detached mode:

`docker compose up -d`

This will:
Start both the backend and frontend containers
Run them in the background

4. To stop the containers:

`docker compose down`


### Option 2 - Using Docker Desktop:

1. Open Docker Desktop
2. Go to the Containers tab
3. Find the project folder name (310-cosc)
4. Click Start to run both the containers
5. Click Stop when done

## Accessing the Services:

Once the containers are running, go to this URL:

  Frontend (REACT+Vite):
  http://localhost:5173/


## Rebuilding the Images (when code or Dockerfile changes):

If you need to rebuild:

`docker compose up --build`

Then start again:
`docker compose up -d`

## Dependencies

| Category              | Component / Technology | Version                |
| --------------------- | ---------------------- | ---------------------- |
| **Frontend**          | React                  | 19.2.0                 |
|                       | React DOM              | 19.2.0                 |
|                       | Vite                   | 7.2.4                  |
|                       | TypeScript             | 5.9.3                  |
| **Backend**           | Python                 | 3.13.7                 |
| **Backend Framework** | FastAPI                | 0.119.1                |
| **Package Manager**   | pip                    | 25.3                   |
| **Database**          | JSON storage           | Included with Python   |
| **Containerization**  | Docker Engine          | 28.4.0 (build d8eb465) |
|                       | Docker Compose         | v2.39.4-desktop.1      |
| **External API**      | TMDB API               | V3                     |

## Backend Requirements
| Package           | Version   |
| ----------------- | --------- |
| annotated-types   | 0.7.0     |
| anyio             | 4.11.0    |
| bandit            | 1.8.6     |
| certifi           | 2025.10.5 |
| click             | 8.3.0     |
| colorama          | 0.4.6     |
| fastapi           | 0.119.1   |
| h11               | 0.16.0    |
| httpcore          | 1.0.9     |
| httpx             | 0.28.1    |
| idna              | 3.11      |
| iniconfig         | 2.3.0     |
| markdown-it-py    | 4.0.0     |
| mdurl             | 0.1.2     |
| packaging         | 25.0      |
| passlib           | 1.7.4     |
| pip               | 25.2      |
| pluggy            | 1.6.0     |
| pydantic          | 2.12.3    |
| pydantic_core     | 2.41.4    |
| Pygments          | 2.19.2    |
| pytest            | 8.4.2     |
| python-multipart  | 0.0.20    |
| PyYAML            | 6.0.3     |
| rich              | 14.2.0    |
| sniffio           | 1.3.1     |
| starlette         | 0.48.0    |
| stevedore         | 5.5.0     |
| typing_extensions | 4.15.0    |
| typing-inspection | 0.4.2     |
| uvicorn           | 0.38.0    |

## Frontend Requirements

| Package                     | Version |
| --------------------------- | ------- |
| @eslint/js                  | 9.39.1  |
| @types/node                 | 24.10.1 |
| @types/react-dom            | 19.2.3  |
| @types/react-router-dom     | 5.3.3   |
| @types/react                | 19.2.7  |
| @vitejs/plugin-react        | 5.1.1   |
| eslint-plugin-react-hooks   | 7.0.1   |
| eslint-plugin-react-refresh | 0.4.24  |
| eslint                      | 9.39.1  |
| globals                     | 16.5.0  |
| react-dom                   | 19.2.0  |
| react-router-dom            | 7.10.0  |
| react                       | 19.2.0  |
| typescript-eslint           | 8.48.0  |
| typescript                  | 5.9.3   |
| vite                        | 7.2.4   |
