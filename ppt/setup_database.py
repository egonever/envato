import os
from datetime import datetime

import pymysql

class DatabaseController:
    def __init__(self):
        self.connect_db()

    def __del__(self):
        self.db.close()

    def connect_db(self):
        self.db = pymysql.connect(host="localhost", user="root", password=None, database="envato")
        self.cursor = pymysql.cursors.DictCursor(self.db)
        self.db.autocommit(True)

    def create_item_table(self):

        self.cursor.execute("DROP TABLE IF EXISTS ppt_item")
        sql = """
            CREATE TABLE ppt_item(
                categories VARCHAR(255),
                contributorUsername VARCHAR(255),
                title VARCHAR(255),
                subTitle VARCHAR(255),
                slug VARCHAR(255),
                tags VARCHAR(255),
                description TEXT(65535),
                fileName VARCHAR(255),
                id VARCHAR(255),
                itemType VARCHAR(255),
                itemTypeName VARCHAR(255),
                itemUuid VARCHAR(255) PRIMARY KEY,
                publishedAt VARCHAR(255),
                updatedAt VARCHAR(255),
                crawled_time DATETIME NOT NULL
                )
        """
        self.cursor.execute(sql)


    def create_image_table(self):
        self.cursor.execute("DROP TABLE IF EXISTS ppt_image")
        sql = """
                CREATE TABLE ppt_image(
                    itemUuid VARCHAR(255) NOT NULL,
                    imgixSubdomain VARCHAR(255) NOT NULL,
                    s3Key VARCHAR(255),
                    og1200x630 VARCHAR(255),
                    og1200x800 VARCHAR(255),
                    tn60x40 VARCHAR(255),
                    tn120x80 VARCHAR(255),
                    tn316x211 VARCHAR(255),
                    tn632x421 VARCHAR(255),
                    w140 VARCHAR(255),
                    w174 VARCHAR(255),
                    w316 VARCHAR(255),
                    w355 VARCHAR(255),
                    w433 VARCHAR(255),
                    w632 VARCHAR(255),
                    w710 VARCHAR(255),
                    w866 VARCHAR(255),
                    w900 VARCHAR(255),
                    w1019 VARCHAR(255),
                    w1170 VARCHAR(255),
                    w1370 VARCHAR(255),
                    w2038 VARCHAR(255),
                    w2740  VARCHAR(255),
                    crawled_time DATETIME NOT NULL,
                    PRIMARY KEY (s3Key)
                    )
                """
        self.cursor.execute(sql)

    def create_downloaded_file_table(self):
        """Create a table contains all the ppt files downloaded

        :return:
        """
        sql = """
                    CREATE TABLE ppt_downloaded(
                        id int NOT NULL AUTO_INCREMENT PRIMARY KEY,
                        fileName VARCHAR(255),
                        size int NOT NULL ,
                        downloaded_time DATETIME NOT NULL
                        )
                """
        self.cursor.execute(sql)

    def synchronize_ppt_store_with_db(self):
        """Put ppt_store files' info into table ppt_downloaded

        :return:
        """

        ppt_store = r"F:\ppt_store"
        files = os.listdir(ppt_store)
        table_name = 'ppt_downloaded'
        columns = 'fileName, size, downloaded_time'
        placeholders = ', '.join(['%s'] * 3)
        query = "INSERT INTO %s ( %s ) VALUES ( %s ) ON DUPLICATE KEY UPDATE downloaded_time=VALUES(downloaded_time)" % (
            table_name, columns, placeholders)
        for file in files:
            data = []
            file_path = os.path.join(ppt_store, file)
            size = os.stat(file_path).st_size
            downloaded_time = os.stat(file_path).st_ctime
            downloaded_time = datetime.utcfromtimestamp(downloaded_time).strftime("%Y-%m-%d %H:%M:%S")
            data.append(file)
            data.append(size)
            data.append(downloaded_time)
            print(f"inserting {file}")
            self.cursor.execute(query, data)
            self.db.commit()

    def synchronize_ppt_downloaded_with_ppt_item(self):
        """Set downloaded field of ppt_item table if fileName is in ppt_downloaded table

        :return:
        """

        sql = "SELECT fileName FROM ppt_downloaded"
        self.cursor.execute(sql)
        files_downloaded_list = self.cursor.fetchall()
        print(len(files_downloaded_list))
        for i in range(len(files_downloaded_list)):
            print(f"Checking {files_downloaded_list[i]['fileName']}")
            is_exist, item_uuid = self.is_file_exist(files_downloaded_list[i]['fileName'])
            if is_exist:
                print("Yes existed")
                query = f"UPDATE ppt_item SET downloaded = TRUE WHERE itemUuid = '{item_uuid}'"
                try:
                    self.cursor.execute(query)
                except Exception as e:
                    if 'MySQL server has gone away' in str(e):
                        self.connect_db()
                        self.cursor.execute(query)
                    else:
                        raise e


    def get_image_urls(self, resolution):
        """Get image urls dict, default resolution is w2740

        :return: list of dict

        image url format f"https://{imgixSubdomain}-0.imgix.net/{s3Key}?{w2740}"
        """

        sql = f"""
         SELECT slug, ppt_item.itemUuid, s3Key, {resolution}, imgixSubdomain FROM ppt_item INNER JOIN ppt_image 
         ON ppt_item.itemUuid = ppt_image.itemUuid WHERE ppt_item.downloaded is TRUE
         """
        image_url = "https://{0}-0.imgix.net/{1}?{2}"
        self.cursor.execute(sql)
        results = self.cursor.fetchall()
        for i in range(len(results)):
            results[i]['url'] = image_url.format(results[i]['imgixSubdomain'], results[i]['s3Key'], results[i][resolution])
        return results


    def is_file_exist(self, file_name):
        """Check if a given file exists in the ppt_item table

        :param file_name: str
        :return: tuple, (True, itemUuid) or (False, None)
        """

        sql = f"SELECT itemUuid FROM ppt_item WHERE fileName='{file_name}'"
        if self.cursor.execute(sql):
            return True, self.cursor.fetchone()['itemUuid']
        else:
            return False, None

    def set_downloaded_field(self, item_uuid):
        """Set the downloaded field of db talbe ppt_item to TRUE

        :param item_uuid:
        :return:
        """

        sql = f"UPDATE ppt_item SET downloaded = TRUE WHERE itemUuid = '{item_uuid}'"
        self.cursor.execute(sql)
        self.db.commit()

    def set_downloaded_field_for_ppt_store(self, ppt_store_dir):
        """Set the downloaded fields to TRUE for all files inside ppt_store_dir

        :param ppt_store_dir: str
        :return:
        """
        files = os.listdir(ppt_store_dir)
        for file in files:
            is_exist, item_uuid = self.is_file_exist(file)
            if is_exist:
                self.set_downloaded_field(item_uuid)

    def get_record(self, table_name, pk):
        sql = f"select * from {table_name} where s3Key = '{pk}'"
        self.cursor.execute(sql)
        result = self.cursor.fetchone()
        print(result)

    def insert_record(self, table_name, item):
        placeholders = ', '.join(['%s'] * len(item))
        columns = ', '.join(item.keys())
        query = "INSERT INTO %s ( %s ) VALUES ( %s ) ON DUPLICATE KEY UPDATE crawled_time=VALUES(crawled_time)" % (
            table_name, columns, placeholders)
        # print(query)
        self.cursor.execute(query, list(item.values()))

    def get_tags_as_dict(self, table_name):
        sql = f"SELECT tags FROM {table_name }"
        self.cursor.execute(sql)
        results = self.cursor.fetchall()
        tags_set = set()
        for elem in results:
            init_set = set(elem['tags'].split(','))
            tags_set.update(init_set)

        # delete tags from set which are not comma separated
        kws = []
        for elem in tags_set:
            if len(elem) > 50 or len(elem) < 4:
                kws.append(elem)
        for kw in kws:
            tags_set.remove(kw)

        tags_dict = {elem: '100' for elem in tags_set}
        return tags_dict



if __name__ == '__main__':
    dbo = DatabaseController()
    # dbo.create_image_table()
    # Synchronize
    dbo.synchronize_ppt_downloaded_with_ppt_item()

    # resolution = 'w2740'
    # results = dbo.get_image_urls(resolution)
    # print(len(results))

    # Synchronize ppt_downloaded with ppt_item
    # dbo.synchronize_ppt_downloaded_with_ppt_item()

    # Check if file exists
    # file_name = "elements-naples-powerpoint-instagram-stories-AQE33HE-2020-05-10.zip"
    # file_name = 'test'
    # is_exist, item_uuid = dbo.is_file_exist(file_name)
    # print(is_exist)
    # print(item_uuid)

    # get single record
    # s3key = '4953b09b-6699-4e56-b009-6fb426c82121'
    # table_name = 'ppt_image'
    # dbo.get_record(table_name, s3key)
    # data = {'itemUuid': '8d4b62d8-6974-4920-9de1-3c6ae77515fe', 'imgixSubdomain': 'elements-cover-images', 's3Key': '4953b09b-6699-4e56-b009-6fb426c82121', 'og1200x630': 'auto=compress&crop=edges&fit=crop&fm=jpeg&h=630&w=1200&s=ad33d5e1bbda80a30fcae4461267d17b', 'og1200x800': 'auto=compress&crop=edges&fit=crop&fm=jpeg&h=800&w=1200&s=61936a95a0bab3aa56f85288a4e6fef3', 'tn60x40': 'crop=top&fit=crop&fm=jpeg&h=40&q=80&w=60&s=eead11c5cf2897075e51a92ffc2b37c3', 'tn120x80': 'crop=top&fit=crop&fm=jpeg&h=80&q=80&w=120&s=6a5b63110c4e8719fddd3e8e5a4323bd', 'tn316x211': 'crop=top&fit=crop&fm=jpeg&h=211&q=80&w=316&s=c7097c452e21ee909a68f95d916a3796', 'tn632x421': 'auto=compress%2Cformat&crop=top&fit=crop&h=421&w=632&s=063ad124a5ae6191f151d9bd851c1a4d', 'w140': 'fit=max&fm=jpeg&q=80&w=140&s=2552a73a658913e18dd6b7fb7d67a2fc', 'w174': 'fit=max&fm=jpeg&q=80&w=174&s=270e8e386237da31a5595379d8a01830', 'w316': 'fit=max&fm=jpeg&q=80&w=316&s=ff008e01ad31b0905261aa5cea76bb79', 'w355': 'fit=max&fm=jpeg&q=80&w=355&s=7a31c12c895cfddee6a4fada3f22c02b', 'w433': 'auto=compress%2Cformat&fit=max&w=433&s=6e545c4e6cd12b91c1273ac69338605b', 'w632': 'auto=compress%2Cformat&fit=max&w=632&s=2e82122b59351af8aaa0ea936c559205', 'w710': 'auto=compress%2Cformat&fit=max&w=710&s=79cb012fe58f9229ecd57c6ca9120326', 'w866': 'auto=compress%2Cformat&fit=max&w=866&s=c853ccd35c499366680ea02fe0a0e51e', 'w900': 'auto=compress%2Cformat&fit=max&w=900&s=c920c36981585e04bbbe655481ae7e23', 'w1019': 'auto=compress%2Cformat&fit=max&w=1019&s=3d5dd811735de6d567a766779c579337', 'w1170': 'auto=compress%2Cformat&fit=max&w=1170&s=2114415c174533a56252a14630d6a014', 'w1370': 'auto=compress%2Cformat&fit=max&w=1370&s=2f03fc2121851a7f7c94b28d714e7082', 'w2038': 'auto=compress%2Cformat&fit=max&w=2038&s=efa48905575d8187bfb219f6f7704e97', 'w2740': 'auto=compress%2Cformat&fit=max&w=2740&s=2f1d7496d1f43e479a27880841c23e34', 'crawled_time': '2022-02-25 11:11:11'}
    # dbo.insert_record(table_name, data)
