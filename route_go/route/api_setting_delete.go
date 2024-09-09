package route

import (
	"log"
	"opennamu/route/tool"

	jsoniter "github.com/json-iterator/go"
)

func Api_setting_delete(call_arg []string) string {
	var json = jsoniter.ConfigCompatibleWithStandardLibrary

	other_set := map[string]string{}
	json.Unmarshal([]byte(call_arg[0]), &other_set)

	db := tool.DB_connect()
	defer db.Close()

	auth_info := tool.Check_acl(db, "", "", "owner_auth", other_set["ip"])

	setting_acl := Setting_list()
	return_data := make(map[string]interface{})

	if _, ok := setting_acl[other_set["set_name"]]; ok {
		if auth_info {
			stmt, err := db.Prepare(tool.DB_change("delete from other where name = ?"))
			if err != nil {
				log.Fatal(err)
			}
			defer stmt.Close()

			_, err = stmt.Exec(other_set["set_name"])
			if err != nil {
				log.Fatal(err)
			}
		} else {
			return_data["response"] = "require auth"
		}
	} else {
		return_data["response"] = "not exist"
	}

	json_data, _ := json.Marshal(return_data)
	return string(json_data)
}
