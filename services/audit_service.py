from services.db import execute_query, execute_update

def log_action(acting_user_id, affected_user_id, action, table_name, record_id, description, previous_value=None, new_value=None):
    query = """
    INSERT INTO Audit_Log (acting_user_id, affected_user_id, action, table_name, record_id, previous_value, new_value, description)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    """
    execute_update(query, (acting_user_id, affected_user_id, action, table_name, record_id, previous_value, new_value, description))

def get_all_audit_logs(limit=100):
    query = """
    SELECT 
        a.log_id,
        a.acting_user_id,
        actor.name AS actor_name,
        actor.email AS actor_email,
        a.affected_user_id,
        target.name AS target_name,
        target.email AS target_email,
        a.action,
        a.table_name,
        a.record_id,
        a.previous_value,
        a.new_value,
        a.description,
        a.action_timestamp
    FROM Audit_Log a
    LEFT JOIN Users actor ON a.acting_user_id = actor.user_id
    LEFT JOIN Users target ON a.affected_user_id = target.user_id
    ORDER BY a.action_timestamp DESC, a.log_id DESC
    LIMIT %s
    """
    return execute_query(query, (limit,), fetch='all')
