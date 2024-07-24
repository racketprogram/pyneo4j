from services.access_control_manager import AccessControlManager

def main():
    acm = AccessControlManager()

    # 定義操作
    operations = [
        "create_database", "delete_database", "read_data", "write_data",
        "manage_users", "view_logs", "configure_system"
    ]
    for op in operations:
        acm.create_operation(op)

    # 創建權限集合
    acm.create_permission_set("db_admin", ["create_database", "delete_database", "read_data", "write_data"])
    acm.create_permission_set("db_operator", ["read_data", "write_data"])
    acm.create_permission_set("system_admin", ["manage_users", "view_logs", "configure_system"])

    # 創建群組
    acm.create_group("Database Administrators")
    acm.create_group("Database Operators")
    acm.create_group("System Administrators")

    # 分配權限集合到群組
    acm.assign_permission_set_to_group("Database Administrators", "db_admin")
    acm.assign_permission_set_to_group("Database Operators", "db_operator")
    acm.assign_permission_set_to_group("System Administrators", "system_admin")

    # 創建用戶
    acm.create_user("Alice")
    acm.create_user("Bob")
    acm.create_user("Charlie")

    # 將用戶添加到群組
    acm.add_user_to_group("Alice", "Database Administrators")
    acm.add_user_to_group("Bob", "Database Operators")
    acm.add_user_to_group("Charlie", "System Administrators")

    # 檢查權限
    print("Alice can create database:", acm.check_user_permission("Alice", "create_database"))
    print("Bob can read data:", acm.check_user_permission("Bob", "read_data"))
    print("Charlie can manage users:", acm.check_user_permission("Charlie", "manage_users"))

    # 獲取用戶所有權限
    print("Alice's permissions:", acm.get_user_permissions("Alice"))
    print("Bob's permissions:", acm.get_user_permissions("Bob"))
    print("Charlie's permissions:", acm.get_user_permissions("Charlie"))

    acm.close()

if __name__ == "__main__":
    main()
    