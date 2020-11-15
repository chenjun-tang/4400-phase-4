-- ID: 2a
-- Author: lvossler3
-- Name: register_student
DROP PROCEDURE IF EXISTS register_student;
DELIMITER //
CREATE PROCEDURE register_student(
		IN i_username VARCHAR(40),
        IN i_email VARCHAR(40),
        IN i_fname VARCHAR(40),
        IN i_lname VARCHAR(40),
        IN i_location VARCHAR(40),
        IN i_housing_type VARCHAR(20),
        IN i_password VARCHAR(40)
)
BEGIN

-- Type solution below
	if not exists (select * from `covidtest_fall2020`.`user` where username = i_username) then
		INSERT INTO `covidtest_fall2020`.`user` VALUES (i_username, MD5(i_password), i_email, i_fname, i_lname);
		INSERT INTO `covidtest_fall2020`.`student` VALUES (i_username, i_housing_type, i_location);
	end if;
-- End of solution
END //
DELIMITER ;

-- ID: 2b
-- Author: lvossler3
-- Name: register_employee
DROP PROCEDURE IF EXISTS register_employee;
DELIMITER //
CREATE PROCEDURE register_employee(
		IN i_username VARCHAR(40),
        IN i_email VARCHAR(40),
        IN i_fname VARCHAR(40),
        IN i_lname VARCHAR(40),
        IN i_phone VARCHAR(10),
        IN i_labtech BOOLEAN,
        IN i_sitetester BOOLEAN,
        IN i_password VARCHAR(40)
)
BEGIN
-- Type solution below
	if not exists (select * from `covidtest_fall2020`.`user` where username = i_username) then
		INSERT INTO `covidtest_fall2020`.`user` VALUES (i_username, MD5(i_password), i_email, i_fname, i_lname);
		INSERT INTO `covidtest_fall2020`.`employee` VALUES (i_username, i_phone);
		if (i_labtech is true and i_sitetester is true) then
			INSERT INTO `covidtest_fall2020`.`labtech` VALUES (i_username);
            INSERT INTO `covidtest_fall2020`.`sitetester` VALUES (i_username);
        elseif (i_labtech is true) then
			INSERT INTO `covidtest_fall2020`.`labtech` VALUES (i_username);
		elseif (i_sitetester is true) then
			INSERT INTO `covidtest_fall2020`.`sitetester` VALUES (i_username);
		end if;
	end if;
-- End of solution
END //
DELIMITER ;

-- ID: 4a
-- Author: Aviva Smith
-- Name: student_view_results
DROP PROCEDURE IF EXISTS `student_view_results`;
DELIMITER //
CREATE PROCEDURE `student_view_results`(
    IN i_student_username VARCHAR(50),
	IN i_test_status VARCHAR(50),
	IN i_start_date DATE,
    IN i_end_date DATE
)
BEGIN
	DROP TABLE IF EXISTS student_view_results_result;
    CREATE TABLE student_view_results_result(
        test_id VARCHAR(7),
        timeslot_date date,
        date_processed date,
        pool_status VARCHAR(40),
        test_status VARCHAR(40)
    );
    INSERT INTO student_view_results_result

    -- Type solution below

		SELECT t.test_id, t.appt_date, p.process_date, p.pool_status , t.test_status
        FROM Appointment a
            LEFT JOIN Test t
                ON t.appt_date = a.appt_date
                AND t.appt_time = a.appt_time
                AND t.appt_site = a.site_name
            LEFT JOIN Pool p
                ON t.pool_id = p.pool_id
        WHERE i_student_username = a.username
            AND (i_test_status = t.test_status OR i_test_status IS NULL)
            AND (i_start_date <= t.appt_date OR i_start_date IS NULL)
            AND (i_end_date >= t.appt_date OR i_end_date IS NULL);

    -- End of solution
END //
DELIMITER ;

-- ID: 5a
-- Author: asmith457
-- Name: explore_results
DROP PROCEDURE IF EXISTS explore_results;
DELIMITER $$
CREATE PROCEDURE explore_results (
    IN i_test_id VARCHAR(7))
BEGIN
    DROP TABLE IF EXISTS explore_results_result;
    CREATE TABLE explore_results_result(
        test_id VARCHAR(7),
        test_date date,
        timeslot time,
        testing_location VARCHAR(40),
        date_processed date,
        pooled_result VARCHAR(40),
        individual_result VARCHAR(40),
        processed_by VARCHAR(80)
    );
    INSERT INTO explore_results_result

    -- Type solution below

        SELECT t.test_id, t.appt_date, t.appt_time, t.appt_site, p.process_date, p.pool_status, t.test_status, concat(u.fname, u.lname) as processed_by
        FROM Test t
            LEFT JOIN Pool p
                ON t.pool_id = p.pool_id
			LEFT JOIN User u
				ON p.processed_by = u.username
		WHERE i_test_id = t.test_id;

    -- End of solution
END$$
DELIMITER ;

-- ID: 6a
-- Author: asmith457
-- Name: aggregate_results
DROP PROCEDURE IF EXISTS aggregate_results;
DELIMITER $$
CREATE PROCEDURE aggregate_results(
    IN i_location VARCHAR(50),
    IN i_housing VARCHAR(50),
    IN i_testing_site VARCHAR(50),
    IN i_start_date DATE,
    IN i_end_date DATE)
BEGIN
    DROP TABLE IF EXISTS aggregate_results_result;
    CREATE TABLE aggregate_results_result(
        test_status VARCHAR(40),
        num_of_test INT,
        percentage DECIMAL(6,2)
    );

    INSERT INTO aggregate_results_result

    -- Type solution below

    select test_status, count(test_status) as num_of_test, convert(100 * count(test.test_status)/T.co,decimal(6,2)) as percentage
	  from test, appointment, student, 
	   (select count(*) as co from test, appointment, student
					where test.appt_site=appointment.site_name
		and test.appt_date = appointment.appt_date
		and test.appt_time = appointment.appt_time
		and appointment.username = student.student_username
					and (i_location is null or location = i_location)
		and (i_housing is null or housing_type = i_housing)
		and (i_testing_site is null or test.appt_site = i_testing_site )
		and (i_start_date is null or test.appt_date >= i_start_date)
		and (i_end_date is null or test.appt_date <= i_end_date)) as T
	  where test.appt_site=appointment.site_name
	   and test.appt_date = appointment.appt_date
	   and test.appt_time = appointment.appt_time
	   and appointment.username = student.student_username
				and (i_location is null or location = i_location)
				and (i_housing is null or housing_type = i_housing)
				and (i_testing_site is null or test.appt_site = i_testing_site )
				and (i_start_date is null or test.appt_date >= i_start_date)
				and (i_end_date is null or test.appt_date <= i_end_date)
	  group by test_status;

    -- End of solution
END$$
DELIMITER ;


-- ID: 7a
-- Author: lvossler3
-- Name: test_sign_up_filter
DROP PROCEDURE IF EXISTS test_sign_up_filter;
DELIMITER //
CREATE PROCEDURE test_sign_up_filter(
    IN i_username VARCHAR(40),
    IN i_testing_site VARCHAR(40),
    IN i_start_date date,
    IN i_end_date date,
    IN i_start_time time,
    IN i_end_time time)
BEGIN
    DROP TABLE IF EXISTS test_sign_up_filter_result;
    CREATE TABLE test_sign_up_filter_result(
        appt_date date,
        appt_time time,
        street VARCHAR (40),
        city VARCHAR(40),
        state VARCHAR(2),
        zip VARCHAR(5),
        site_name VARCHAR(40));
        
	
    INSERT INTO test_sign_up_filter_result

    -- Type solution below
    
    select appt_date, appt_time, street, city, state, zip, site.site_name
	from appointment,site, student
	where appointment.site_name = site.site_name
         and (i_username is NULL or (student.student_username=i_username and student.location=site.location))
         and (appointment.username IS NULL) and (i_testing_site IS NULL or site.site_name = i_testing_site )
         and (i_start_date IS NULL or appt_date >= i_start_date) and (i_end_date IS NULL or appt_date <=i_end_date)
         and (i_start_time IS NULL  or appt_time >= i_start_time) and (i_end_time IS NULL or appt_time <= i_end_time);

    -- End of solution

    END //
    DELIMITER ;

-- ID: 7b
-- Author: lvossler3
-- Name: test_sign_up
DROP PROCEDURE IF EXISTS test_sign_up;
DELIMITER //
CREATE PROCEDURE test_sign_up(
		IN i_username VARCHAR(40),
        IN i_site_name VARCHAR(40),
        IN i_appt_date date,
        IN i_appt_time time,
        IN i_test_id VARCHAR(7)
)
BEGIN
-- Type solution below
	declare count_active_sign_up int default
		(select count(*) from appointment,test
		where username=i_username 
			and appointment.appt_date = test.appt_date
			and appointment.appt_time = test.appt_time
			and appointment.site_name = test.appt_site
			and test_status = 'pending');

    -- declare new_test_id int default(select max(test_id)+1 from test);
	declare filled varchar(40) default(select username 
								from appointment where site_name = i_site_name 
													and appt_date=i_appt_date and appt_time=i_appt_time);
    -- user can only have one active(pending) signup
    if(count_active_sign_up < 1 and filled is null) then
		update appointment set username = i_username
		where site_name = i_site_name and appt_date=i_appt_date and appt_time=i_appt_time;
		
		insert into test
		values(i_test_id, 'pending',null,i_site_name, i_appt_date,i_appt_time);
	else
		select "User cannot sign up this test. Reason: This appointment has been filled/One user could only have one active(pending) signup." as log;
	end if;

-- End of solution
END //
DELIMITER ;

-- Number: 8a
-- Author: lvossler3
-- Name: tests_processed
DROP PROCEDURE IF EXISTS tests_processed;
DELIMITER //
CREATE PROCEDURE tests_processed(
    IN i_start_date date,
    IN i_end_date date,
    IN i_test_status VARCHAR(10),
    IN i_lab_tech_username VARCHAR(40))
BEGIN
    DROP TABLE IF EXISTS tests_processed_result;
    CREATE TABLE tests_processed_result(
        test_id VARCHAR(7),
        pool_id VARCHAR(10),
        test_date date,
        process_date date,
        test_status VARCHAR(10) );
    INSERT INTO tests_processed_result
    -- Type solution below

        select test_id, test.pool_id, appt_date, process_date, test_status 
		from test, pool
		where test.pool_id = pool.pool_id 
			and (i_start_date is null or appt_date>=i_start_date)
			and (i_end_date is null or appt_date<=i_end_date) 
            and(i_test_status is null or test_status = i_test_status)
            and (i_lab_tech_username is null or processed_by = i_lab_tech_username);

    -- End of solution
    END //
    DELIMITER ;

-- ID: 9a
-- Author: ahatcher8@
-- Name: view_pools
DROP PROCEDURE IF EXISTS view_pools;
DELIMITER //
CREATE PROCEDURE view_pools(
    IN i_begin_process_date DATE,
    IN i_end_process_date DATE,
    IN i_pool_status VARCHAR(20),
    IN i_processed_by VARCHAR(40)
)
BEGIN
    DROP TABLE IF EXISTS view_pools_result;
    CREATE TABLE view_pools_result(
        pool_id VARCHAR(10),
        test_ids VARCHAR(100),
        date_processed DATE,
        processed_by VARCHAR(40),
        pool_status VARCHAR(20));

    INSERT INTO view_pools_result
-- Type solution below

    SELECT pool.pool_id, group_concat(test_id) as test_ids, process_date, processed_by, pool_status 
        from pool,test
        where pool.pool_id = test.pool_id
			and (i_begin_process_date is null or (process_date>= i_begin_process_date or process_date is null))
			and (i_end_process_date is null or process_date<= i_end_process_date)
            and (i_pool_status is null or pool_status = i_pool_status)
            and (i_processed_by is null or pool.processed_by like concat( '%' ,i_processed_by, '%' ))
		group by pool.pool_id;

-- End of solution
END //
DELIMITER ;

-- ID: 10a
-- Author: ahatcher8@
-- Name: create_pool
DROP PROCEDURE IF EXISTS create_pool;
DELIMITER //
CREATE PROCEDURE create_pool(
	IN i_pool_id VARCHAR(10),
    IN i_test_id VARCHAR(7)
)
BEGIN
-- Type solution below
	declare has_test int default(
		select count(*) from test
		where test_id = i_test_id and pool_id is null);
	
    -- one pool at least have one available test
    if(has_test = 1) then
    
		insert into pool 
		values (i_pool_id, 'pending', NULL, NULL);
		
		update test set pool_id = i_pool_id
		where test_id = i_test_id;
	else
		select "We could not create this pool. Reason: The test has been assigned to a pool./The test does not exist." as log;
	end if;

-- End of solution
END //
DELIMITER ;

-- ID: 10b
-- Author: ahatcher8@
-- Name: assign_test_to_pool
DROP PROCEDURE IF EXISTS assign_test_to_pool;
DELIMITER //
CREATE PROCEDURE assign_test_to_pool(
    IN i_pool_id VARCHAR(10),
    IN i_test_id VARCHAR(7)
)
BEGIN
-- Type solution below
	declare tests_count int default (select count(*) from test
					where pool_id = i_pool_id);
    declare has_test int default(
		select count(*) from test
			where test_id = i_test_id and pool_id is null);                
	if (tests_count >= 1 and tests_count <= 6 and has_test=1) then
		update test set pool_id = i_pool_id
		where test_id = i_test_id;
    else
		select "We could not assign this test to the pool. Reason: A pool could not have more than 7 tests./ The test does not exist./ The test has been assigned to another pool.)" as log;
	
	end if;

-- End of solution
END //
DELIMITER ;

-- ID: 11a
-- Author: ahatcher8@
-- Name: process_pool
DROP PROCEDURE IF EXISTS process_pool;
DELIMITER //
CREATE PROCEDURE process_pool(
    IN i_pool_id VARCHAR(10),
    IN i_pool_status VARCHAR(20),
    IN i_process_date DATE,
    IN i_processed_by VARCHAR(40)
)
BEGIN
-- Type solution below

    SELECT pool_status
    INTO @curr_status
    FROM POOL
    WHERE pool_id = i_pool_id;

    IF
        ((@curr_status = 'pending') AND (i_pool_status = 'positive' OR i_pool_status = 'negative'))
    THEN
        UPDATE POOL
        SET pool_status = i_pool_status, process_date = i_process_date, processed_by = i_processed_by
        WHERE pool_id = i_pool_id;
    END IF;


-- End of solution
END //
DELIMITER ;

-- ID: 11b
-- Author: ahatcher8@
-- Name: process_test
DROP PROCEDURE IF EXISTS process_test;
DELIMITER //
CREATE PROCEDURE process_test(
    IN i_test_id VARCHAR(7),
    IN i_test_status VARCHAR(20)
)
BEGIN
-- Type solution below
	SELECT test_status, pool_id
    INTO @curr_status, @i_pool_id
    FROM TEST
    WHERE test_id = i_test_id;

    SELECT pool_status
    INTO @curr_pool_status
    FROM POOL
    WHERE pool_id = @i_pool_id;

    IF
        ((@curr_pool_status = 'positive' OR (@curr_pool_status = 'negative' AND i_test_status = 'negative')) AND (@curr_status = 'pending') AND (i_test_status = 'positive' OR i_test_status = 'negative'))
    THEN
        UPDATE TEST
        SET test_status = i_test_status
        WHERE test_id = i_test_id;
    END IF;

-- End of solution
END //
DELIMITER ;

-- ID: 12a
-- Author: dvaidyanathan6
-- Name: create_appointment

DROP PROCEDURE IF EXISTS create_appointment;
DELIMITER //
CREATE PROCEDURE create_appointment(
	IN i_site_name VARCHAR(40),
    IN i_date DATE,
    IN i_time TIME
)
BEGIN
-- Type solution below
	SELECT COUNT(*)
    INTO @appointment_num
    FROM APPOINTMENT
    WHERE site_name = i_site_name AND appt_date = i_date;

    SELECT COUNT(*)
    INTO @tester_num
    FROM WORKING_AT
    WHERE site = i_site_name;

    IF
        (@appointment_num < 10*@tester_num AND NOT EXISTS (SELECT * FROM APPOINTMENT WHERE site_name = i_site_name AND appt_date = i_date AND appt_time = i_time))
    THEN
        INSERT INTO APPOINTMENT
		VALUES (NULL, i_site_name, i_date, i_time);
    END IF;
-- End of solution
END //
DELIMITER ;

-- ID: 13a
-- Author: dvaidyanathan6@
-- Name: view_appointments
DROP PROCEDURE IF EXISTS view_appointments;
DELIMITER //
CREATE PROCEDURE view_appointments(
    IN i_site_name VARCHAR(40),
    IN i_begin_appt_date DATE,
    IN i_end_appt_date DATE,
    IN i_begin_appt_time TIME,
    IN i_end_appt_time TIME,
    IN i_is_available INT  -- 0 for "booked only", 1 for "available only", NULL for "all"
)
BEGIN
    DROP TABLE IF EXISTS view_appointments_result;
    CREATE TABLE view_appointments_result(

        appt_date DATE,
        appt_time TIME,
        site_name VARCHAR(40),
        location VARCHAR(40),
        username VARCHAR(40));

    INSERT INTO view_appointments_result
-- Type solution below

	SELECT appt_date, appt_time, site_name, location, username
	FROM APPOINTMENT NATURAL JOIN SITE
	WHERE (i_site_name IS NULL OR site_name = i_site_name)
		AND (i_begin_appt_date IS NULL OR appt_date >= i_begin_appt_date)
		AND (i_end_appt_date IS NULL OR appt_date <= i_end_appt_date)
		AND (i_begin_appt_time IS NULL OR appt_time >= i_begin_appt_time)
		AND (i_end_appt_time IS NULL OR appt_time <= i_end_appt_time)
		AND (i_is_available IS NULL
			OR (i_is_available = 0 AND username IS NOT NULL)
            OR (i_is_available = 1 AND username IS NULL));

-- End of solution
END //
DELIMITER ;


-- ID: 14a
-- Author: kachtani3@
-- Name: view_testers
DROP PROCEDURE IF EXISTS view_testers;
DELIMITER //
CREATE PROCEDURE view_testers()
BEGIN
    DROP TABLE IF EXISTS view_testers_result;
    CREATE TABLE view_testers_result(

        username VARCHAR(40),
        name VARCHAR(80),
        phone_number VARCHAR(10),
        assigned_sites VARCHAR(255));

    INSERT INTO view_testers_result
-- Type solution below

    SELECT sitetester_username as username, concat(fname, ' ', lname) as 'name', phone_num as 'phone_number', group_concat(site ORDER BY site ASC) as 'assigned_sites'
    FROM ((SITETESTER JOIN EMPLOYEE ON sitetester_username = emp_username) JOIN USER ON sitetester_username = username) LEFT OUTER JOIN WORKING_AT ON sitetester_username = WORKING_AT.username
    GROUP BY sitetester_username;
-- End of solution
END //
DELIMITER ;

-- ID: 15a
-- Author: kachtani3@
-- Name: create_testing_site
DROP PROCEDURE IF EXISTS create_testing_site;
DELIMITER //
CREATE PROCEDURE create_testing_site(
	IN i_site_name VARCHAR(40),
    IN i_street varchar(40),
    IN i_city varchar(40),
    IN i_state char(2),
    IN i_zip char(5),
    IN i_location varchar(40),
    IN i_first_tester_username varchar(40)
)
BEGIN
-- Type solution below
	IF
        (EXISTS (SELECT * FROM SITETESTER WHERE sitetester_username = i_first_tester_username) 
        AND NOT EXISTS (SELECT * FROM SITE WHERE site_name = i_site_name)
        AND EXISTS (SELECT * FROM LOCATION WHERE location_name = i_location)
        AND i_site_name IS NOT NULL
        AND i_street IS NOT NULL
        AND i_city IS NOT NULL
        AND i_zip IS NOT NULL AND length(i_zip) = 5
        AND i_location IS NOT NULL
        AND i_state IS NOT NULL)
        AND i_first_tester_username IS NOT NULL
    THEN
        INSERT INTO SITE
		VALUES (i_site_name, i_street, i_city, i_state, i_zip, i_location);
        INSERT INTO WORKING_AT
        VALUES (i_first_tester_username, i_site_name);
    END IF;


-- End of solution
END //
DELIMITER ;

-- ID: 16a
-- Author: kachtani3@
-- Name: pool_metadata
DROP PROCEDURE IF EXISTS pool_metadata;
DELIMITER //
CREATE PROCEDURE pool_metadata(
    IN i_pool_id VARCHAR(10))
BEGIN
    DROP TABLE IF EXISTS pool_metadata_result;
    CREATE TABLE pool_metadata_result(
        pool_id VARCHAR(10),
        date_processed DATE,
        pooled_result VARCHAR(20),
        processed_by VARCHAR(100));

    INSERT INTO pool_metadata_result
-- Type solution below
    SELECT pool_id, process_date, pool_status, concat(fname, ' ', lname) as 'name'
	from POOL, USER
	where pool_id = i_pool_id and username = processed_by;
    

-- End of solution
END //
DELIMITER ;

-- ID: 16b
-- Author: kachtani3@
-- Name: tests_in_pool
DROP PROCEDURE IF EXISTS tests_in_pool;
DELIMITER //
CREATE PROCEDURE tests_in_pool(
    IN i_pool_id VARCHAR(10))
BEGIN
    DROP TABLE IF EXISTS tests_in_pool_result;
    CREATE TABLE tests_in_pool_result(
        test_id varchar(7),
        date_tested DATE,
        testing_site VARCHAR(40),
        test_result VARCHAR(20));

    INSERT INTO tests_in_pool_result
-- Type solution below

    SELECT test_id, appt_date, appt_site, test_status 
    from test
	where pool_id = i_pool_id;
-- End of solution
END //
DELIMITER ;

-- ID: 17a
-- Author: kachtani3@
-- Name: tester_assigned_sites
DROP PROCEDURE IF EXISTS tester_assigned_sites;
DELIMITER //
CREATE PROCEDURE tester_assigned_sites(
    IN i_tester_username VARCHAR(40))
BEGIN
    DROP TABLE IF EXISTS tester_assigned_sites_result;
    CREATE TABLE tester_assigned_sites_result(
        site_name VARCHAR(40));

    INSERT INTO tester_assigned_sites_result
-- Type solution below
	select site from WORKING_AT, site
	where site_name = site and username = i_tester_username;

-- End of solution
END //
DELIMITER ;

-- ID: 17b
-- Author: kachtani3@
-- Name: assign_tester
DROP PROCEDURE IF EXISTS assign_tester;
DELIMITER //
CREATE PROCEDURE assign_tester(
	IN i_tester_username VARCHAR(40),
    IN i_site_name VARCHAR(40)
)
BEGIN
-- Type solution below
insert INTO WORKING_AT VALUES
(i_tester_username, i_site_name);

-- End of solution
END //
DELIMITER ;


-- ID: 17c
-- Author: kachtani3@
-- Name: unassign_tester
DROP PROCEDURE IF EXISTS unassign_tester;
DELIMITER //
CREATE PROCEDURE unassign_tester(
	IN i_tester_username VARCHAR(40),
    IN i_site_name VARCHAR(40)
)
BEGIN
-- Type solution below
	IF
		(select count(*) from WORKING_AT where site = i_site_name) > 1
	THEN
		DELETE FROM WORKING_AT
        WHERE username = i_tester_username and site = i_site_name;
    END IF;

-- End of solution
END //
DELIMITER ;


-- ID: 18a
-- Author: lvossler3
-- Name: daily_results
DROP PROCEDURE IF EXISTS daily_results;
DELIMITER //
CREATE PROCEDURE daily_results()
BEGIN
	DROP TABLE IF EXISTS daily_results_result;
    CREATE TABLE daily_results_result(
		process_date date,
        num_tests int,
        pos_tests int,
        pos_percent DECIMAL(6,2));
	INSERT INTO daily_results_result
    -- Type solution below

    SELECT p.process_date,  count(test_id) as num_tests, sum(test_status = 'positive') as pos_tests,
    round(((sum(test_status = 'positive'))/count(test_status))*100, 2)as pos_percent
    from test
		LEFT JOIN pool p
			ON p.pool_id = test.pool_id
    group by p.process_date
    having p.process_date is not null;

    -- End of solution
    END //
    DELIMITER ;

