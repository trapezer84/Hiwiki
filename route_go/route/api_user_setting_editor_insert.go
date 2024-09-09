package route

import (
	"log"
	"opennamu/route/tool"

	jsoniter "github.com/json-iterator/go"
)

func Api_user_setting_editor_post(call_arg []string) string {
	var json = jsoniter.ConfigCompatibleWithStandardLibrary

	other_set := map[string]string{}
	json.Unmarshal([]byte(call_arg[0]), &other_set)

	db := tool.DB_connect()
	defer db.Close()

	ip := other_set["ip"]

	if !tool.IP_or_user(ip) {
		stmt, err := db.Prepare(tool.DB_change("insert into user_set (id, name, data) values (?, 'user_editor_top', ?)"))
		if err != nil {
			log.Fatal(err)
		}
		defer stmt.Close()

		_, err = stmt.Exec(ip, other_set["data"])
		if err != nil {
			log.Fatal(err)
		}

		return_data := make(map[string]interface{})
		return_data["response"] = "ok"
		return_data["language"] = map[string]string{
			"save": tool.Get_language(db, "save", false),
		}

		json_data, _ := json.Marshal(return_data)
		return string(json_data)
	} else {
		return_data := make(map[string]interface{})
		return_data["response"] = "require auth"
		return_data["language"] = map[string]string{
			"authority_error": tool.Get_language(db, "authority_error", false),
		}

		json_data, _ := json.Marshal(return_data)
		return string(json_data)
	}
}
