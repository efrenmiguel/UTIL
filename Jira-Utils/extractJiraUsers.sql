
SELECT 
	u.lower_user_name,
	u.active,
	u.created_date,
	u.lower_first_name,
	u.lower_last_name,
	u.lower_email_address,
	u.display_name,
	m.user_groups,
	(CASE WHEN a.attribute_value IS NOT NULL
		THEN TO_DATE('19700101','yyyymmdd') + 
			((a.attribute_value/1000)/24/60/60) as last_login_date
		ELSE NULL
	END) AS last_login_date,
	d.directory_name,
	d.directory_position
FROM 
	cwd_user u
	LEFT JOIN (
		SELECT child_id, directory_id, LISTAGG(parent_name, ', ') AS user_groups
		FROM cwd_membership
		GROUP BY child_id, directory_id
		) m 
		ON m.child_id = u.ID 
			AND m.directory_id = u.directory_id
	LEFT JOIN (
		SELECT user_id, attribute_value
		FROM cwd_user_attributes
		WHERE attribute_name = 'login.lastLoginMillis'
		) a 
		ON a.user_id = u.ID
	LEFT JOIN cwd_directory d 
		ON d.ID = u.directory_id
			AND d.active = 1
ORDER BY 
	u.ID, d.directory_position
;
