package route

import (
	"database/sql"
	"log"
	"opennamu/route/tool"
	"strings"

	jsoniter "github.com/json-iterator/go"
)

func Api_bbs_w_comment_one(call_arg []string) string {
	var json = jsoniter.ConfigCompatibleWithStandardLibrary

	other_set := map[string]string{}
	json.Unmarshal([]byte(call_arg[0]), &other_set)

	db := tool.DB_connect()
	defer db.Close()

	sub_code := other_set["sub_code"]
	sub_code_parts := strings.Split(sub_code, "-")
	sub_code_last := ""
	new_sub_code := ""

	if other_set["tool"] == "around" {
		new_sub_code = other_set["sub_code"]
	} else {
		if len(sub_code_parts) > 2 {
			sub_code_last = sub_code_parts[len(sub_code_parts)-1]
			sub_code_parts = sub_code_parts[:len(sub_code_parts)-1]

			new_sub_code = strings.Join(sub_code_parts, "-")
		}
	}

	var rows *sql.Rows
	if other_set["tool"] == "around" {
		stmt, err := db.Prepare(tool.DB_change("select set_name, set_data, set_code, set_id from bbs_data where (set_name = 'comment' or set_name like 'comment%') and set_id = ?"))
		if err != nil {
			log.Fatal(err)
		}
		defer stmt.Close()

		rows, err = stmt.Query(new_sub_code)
		if err != nil {
			log.Fatal(err)
		}
	} else {
		stmt, err := db.Prepare(tool.DB_change("select set_name, set_data, set_code, set_id from bbs_data where (set_name = 'comment' or set_name like 'comment%') and set_id = ? and set_code = ?"))
		if err != nil {
			log.Fatal(err)
		}
		defer stmt.Close()

		rows, err = stmt.Query(new_sub_code, sub_code_last)
		if err != nil {
			log.Fatal(err)
		}
	}
	defer rows.Close()

	data_list := []map[string]string{}
	temp_dict := map[string]string{}
	before_set_code := ""

	for rows.Next() {
		var set_name string
		var set_data string
		var set_code string
		var set_id string

		err := rows.Scan(&set_name, &set_data, &set_code, &set_id)
		if err != nil {
			log.Fatal(err)
		}

		if before_set_code != set_code {
			if before_set_code != "" {
				data_list = append(data_list, temp_dict)
			}

			temp_dict = map[string]string{}
			temp_dict["id"] = set_id
			temp_dict["code"] = set_code

			before_set_code = set_code
		}

		temp_dict[set_name] = set_data
	}

	if before_set_code != "" {
		data_list = append(data_list, temp_dict)
	}

	if other_set["legacy"] != "" {
		json_data, _ := json.Marshal(data_list)
		return string(json_data)
	} else {
		return_data := make(map[string]interface{})
		return_data["data"] = data_list

		json_data, _ := json.Marshal(return_data)
		return string(json_data)
	}
}
