from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
import models
import schemas

# ---------------------------------------------------------
# FUNCTION: Retrieve a single task from the database using its ID
# ---------------------------------------------------------
def get_task(db: Session, task_id: int):
    # db.query(models.Task) → access the "tasks" table
    # filter(...) → apply condition (WHERE id = task_id)
    # first() → return the first match or None if not found
    return db.query(models.Task).filter(models.Task.id == task_id).first()


# ---------------------------------------------------------
# FUNCTION: Retrieve all tasks from the database
# ---------------------------------------------------------
def get_tasks(db: Session, skip: int = 0, limit: int = 100):
    # Currently returns all tasks without pagination
    # NOTE: skip and limit are defined but not used (can be improved)
    return db.query(models.Task).offset(skip).limit(limit).all()


# ---------------------------------------------------------
# FUNCTION: Create a new task and store it in the database
# ---------------------------------------------------------
def create_task(db: Session, task: schemas.TaskCreate):
    try:
        db_task = models.Task(
            title=task.title,
            description=task.description,
            deadline=task.deadline,
            status=task.status.value
        )
        db.add(db_task)
        db.commit()
        db.refresh(db_task)
        return db_task
    except SQLAlchemyError:
        db.rollback()
        raise

    # Add the new task to the database session (not yet saved)
    db.add(db_task)

    # Commit the transaction → actually writes data into the database
    db.commit()

    # Refresh the object → retrieves updated data (e.g., generated ID)
    db.refresh(db_task)

    # Return the created task (will be converted to JSON by FastAPI)
    return db_task


# ---------------------------------------------------------
# FUNCTION: update_task
# الهدف: Update an existing task (partial update supported)
# ---------------------------------------------------------
def update_task(db: Session, task_id: int, task: schemas.TaskUpdate):
    # Step 1: Retrieve the task from the database
    db_task = db.query(models.Task).filter(models.Task.id == task_id).first()

    # If the task does not exist, return None
    if not db_task:
        return None

    # Step 2: Extract only fields provided by the user
    # exclude_unset=True ensures we only update sent fields
    update_data = task.model_dump(exclude_unset=True)

    # Step 3: Loop through provided fields and update dynamically
    for key, value in update_data.items():

        # Special case: status is an Enum → convert to string
        if key == 'status' and value is not None:
            setattr(db_task, key, value.value)
        else:
            # setattr allows dynamic attribute assignment
            # Example: db_task.title = "New Title"
            setattr(db_task, key, value)

    # Step 4: Save changes to the database
    db.commit()

    # Refresh object to get latest state
    db.refresh(db_task)

    # Return updated task
    return db_task


# ---------------------------------------------------------
# FUNCTION: Delete a task from the database using its ID
# ---------------------------------------------------------
def delete_task(db: Session, task_id: int):
    # Step 1: Retrieve the task
    db_task = db.query(models.Task).filter(models.Task.id == task_id).first()

    # Step 2: If task exists → delete it
    if db_task:
        # Mark the object for deletion
        db.delete(db_task)

        # Commit the transaction → apply deletion in DB
        db.commit()

        # Return True to indicate success
        return True

    # If task does not exist → return False
    return False