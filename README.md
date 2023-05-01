# TTM4115_Project

## Dependencies

We assume you are running python 3.8 or higher.

Run

```bash
pip install -r requirements.txt
```

## Running the system

The system mainly consists of 3 major parts, namely the instructor, the student and the server. Each of these match to one of the devices in our
deployment diagram, and have their own script as an entrypoint. To run each system see below

### Student

```bash
python student.py
```

### Instructor

```bash
python instructor.py
```

### Server

```bash
python server.py
```
