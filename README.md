
# IoT Stream Data Collection and Validation

This project consumes IoT stream data from a simulated python script that writes data to a port.

The ingestion data is first validated for its type using pydantic and saved in a local SQLAlchemy database.

Multiple endpoints are provided to view the data along with query parameters to further filter it.

## Steps to run the project:
1. **Build the docker image**: `docker build -t iot-fastapi:1 .`
2. **Run the Container**: `docker run --rm -it --name iot-fastapi-dev -p 8001:8000 iot-fastapi:1`
3. Open the link displayed in the terminal and check for `"status": "online"` message right after it loads.
4. Open another terminal and head to ./scripts and run `python simulate_stream.py`
5. Check the endpoints at `/readings` to get the readings after the container started.
6. Head over to `/docs` to find other useful endpoints and use.
