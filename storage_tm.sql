-- MySQL dump 10.13  Distrib 5.5.23, for Win64 (x86)
--
-- Host: localhost    Database: storage_tm
-- ------------------------------------------------------
-- Server version	5.5.23

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `discip`
--

DROP TABLE IF EXISTS `discip`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `discip` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `id_spec` int(11) NOT NULL,
  `name` varchar(200) COLLATE utf8_unicode_ci DEFAULT NULL,
  `eduYear` int(1) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `id_spec2` (`id_spec`),
  CONSTRAINT `id_spec2` FOREIGN KEY (`id_spec`) REFERENCES `spec` (`id`) ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=369 DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `discip`
--

LOCK TABLES `discip` WRITE;
/*!40000 ALTER TABLE `discip` DISABLE KEYS */;

/*!40000 ALTER TABLE `discip` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `files`
--

DROP TABLE IF EXISTS `files`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `files` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `id_user` int(11) NOT NULL,
  `id_discip` int(11) NOT NULL,
  `id_role` int(11) NOT NULL,
  `id_tmtypes` int(11) NOT NULL DEFAULT '1',
  `id_pertain` int(11) NOT NULL,
  `name` varchar(200) COLLATE utf8_unicode_ci NOT NULL,
  `name_hash` varchar(50) COLLATE utf8_unicode_ci DEFAULT NULL,
  `timestamp` datetime DEFAULT NULL,
  `info` varchar(500) COLLATE utf8_unicode_ci DEFAULT NULL,
  `eduYear` int(1) DEFAULT NULL,
  `public` int(1) NOT NULL DEFAULT '0',
  `accept` int(1) NOT NULL DEFAULT '0',
  PRIMARY KEY (`id`),
  KEY `id_user2` (`id_user`),
  KEY `id_discip1` (`id_discip`),
  KEY `id_role3` (`id_role`),
  KEY `id_tmtypes1` (`id_tmtypes`),
  KEY `id_pertain1` (`id_pertain`),
  CONSTRAINT `id_discip1` FOREIGN KEY (`id_discip`) REFERENCES `discip` (`id`) ON UPDATE CASCADE,
  CONSTRAINT `id_pertain` FOREIGN KEY (`id_pertain`) REFERENCES `pertain` (`id`) ON UPDATE CASCADE,
  CONSTRAINT `id_pertain1` FOREIGN KEY (`id_pertain`) REFERENCES `pertain` (`id`) ON UPDATE CASCADE,
  CONSTRAINT `id_role3` FOREIGN KEY (`id_role`) REFERENCES `role` (`id`) ON UPDATE CASCADE,
  CONSTRAINT `id_tmtypes1` FOREIGN KEY (`id_tmtypes`) REFERENCES `tmtypes` (`id`) ON UPDATE CASCADE,
  CONSTRAINT `id_user2` FOREIGN KEY (`id_user`) REFERENCES `user` (`id`) ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=108 DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `files`
--

LOCK TABLES `files` WRITE;
/*!40000 ALTER TABLE `files` DISABLE KEYS */;
/*!40000 ALTER TABLE `files` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `groups`
--

DROP TABLE IF EXISTS `groups`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `groups` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `id_spec` int(11) NOT NULL,
  `name` varchar(10) COLLATE utf8_unicode_ci NOT NULL,
  PRIMARY KEY (`id`),
  KEY `id_spec3` (`id_spec`),
  CONSTRAINT `id_spec3` FOREIGN KEY (`id_spec`) REFERENCES `spec` (`id`) ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `groups`
--

LOCK TABLES `groups` WRITE;
/*!40000 ALTER TABLE `groups` DISABLE KEYS */;
INSERT INTO `groups` VALUES (2,2,'');
/*!40000 ALTER TABLE `groups` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `message`
--

DROP TABLE IF EXISTS `message`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `message` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `message` varchar(700) COLLATE utf8_unicode_ci DEFAULT NULL,
  `timestamp` datetime DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `message`
--

LOCK TABLES `message` WRITE;
/*!40000 ALTER TABLE `message` DISABLE KEYS */;
INSERT INTO `message` VALUES (1,'Сообщение для преподавателей ведущих специалистов и методистов.','2014-11-25 16:36:28');
/*!40000 ALTER TABLE `message` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `method`
--

DROP TABLE IF EXISTS `method`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `method` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(50) COLLATE utf8_unicode_ci NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=11 DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `method`
--

LOCK TABLES `method` WRITE;
/*!40000 ALTER TABLE `method` DISABLE KEYS */;
INSERT INTO `method` VALUES (1,'Администрация'),(2,''),(4,'Общих гуманитарных и социально-экономических дисци'),(5,'Естественно-научных и математических дисциплин'),(6,'Физвоспитания и ОБЖ'),(8,'Строительных дисциплин'),(9,'Экономических дисциплин'),(10,'Электро-технических дисциплин');
/*!40000 ALTER TABLE `method` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `pertain`
--

DROP TABLE IF EXISTS `pertain`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `pertain` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(100) COLLATE utf8_unicode_ci NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `pertain`
--

LOCK TABLES `pertain` WRITE;
/*!40000 ALTER TABLE `pertain` DISABLE KEYS */;
INSERT INTO `pertain` VALUES (1,'По колледжу'),(2,'По специальности'),(3,'По дисциплине');
/*!40000 ALTER TABLE `pertain` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `role`
--

DROP TABLE IF EXISTS `role`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `role` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(15) COLLATE utf8_unicode_ci DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `role`
--

LOCK TABLES `role` WRITE;
/*!40000 ALTER TABLE `role` DISABLE KEYS */;
INSERT INTO `role` VALUES (1,'Студент'),(2,'Преподаватель'),(3,'Администратор'),(4,'Вед.специалист'),(5,'Методист');
/*!40000 ALTER TABLE `role` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `spec`
--

DROP TABLE IF EXISTS `spec`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `spec` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(200) COLLATE utf8_unicode_ci DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=17 DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `spec`
--

LOCK TABLES `spec` WRITE;
/*!40000 ALTER TABLE `spec` DISABLE KEYS */;
INSERT INTO `spec` VALUE (2,'');
/*!40000 ALTER TABLE `spec` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `tmtypes`
--

DROP TABLE IF EXISTS `tmtypes`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `tmtypes` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `id_pertain` int(11) NOT NULL,
  `name` varchar(100) COLLATE utf8_unicode_ci DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `id_pertain2` (`id_pertain`),
  CONSTRAINT `id_pertain2` FOREIGN KEY (`id_pertain`) REFERENCES `pertain` (`id`) ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=39 DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tmtypes`
--

LOCK TABLES `tmtypes` WRITE;
/*!40000 ALTER TABLE `tmtypes` DISABLE KEYS */;
INSERT INTO `tmtypes` VALUES (1,1,'По колледжу'),(2,2,'ОПОП по специальности'),(3,2,'Рецензии работодателей на ОПОП'),(4,2,'Отчеты о качестве реализуемых дисциплин'),(5,2,'Метод. указания по проведению занятий в интерактивных формах'),(6,2,'Программа практик'),(16,2,'Программа итоговой государственной аттестации'),(17,2,'Метод. указания по выполнению выпускных квалификационных работ'),(18,2,'Фонд оценочных средств для проведения итоговой аттестации'),(19,2,'Результаты итоговой аттестации'),(20,2,'Отчеты председателей ГАК'),(23,3,'Рабочая программа дисциплины'),(24,3,'Метод. рекомендации по предмету'),(25,3,'Метод. указания студентам по изучению учебной дисциплины'),(26,3,'Технологические карты'),(27,3,'Контрольно-оценочные средства'),(28,3,'Метод. указания и задания к самостоятельной работе студентов'),(29,3,'Метод.указания по выполнению контрольных работ'),(30,3,'Метод.указания по выполнению курсовых работ'),(31,3,'Комплекты КОС для проведения комплексного экзамена по проф.модулю'),(32,3,'Метод.комплект входного контроля знаний'),(33,3,'Тексты лекций (или их краткое содержание)'),(34,3,'Слайд-презентации'),(35,3,'Метод.указания по выполнению лабораторных работ'),(36,3,'Практикум'),(37,3,'Сборник ситуационных задач'),(38,3,'Материалы к аттестации');
/*!40000 ALTER TABLE `tmtypes` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `user`
--

DROP TABLE IF EXISTS `user`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `user` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `id_spec` int(11) NOT NULL,
  `id_method` int(11) NOT NULL,
  `id_role` int(11) NOT NULL,
  `id_group` int(11) NOT NULL,
  `name` varchar(50) COLLATE utf8_unicode_ci NOT NULL,
  `login` varchar(50) COLLATE utf8_unicode_ci NOT NULL,
  `password_hash` varchar(128) COLLATE utf8_unicode_ci DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `id_spec1` (`id_spec`),
  KEY `id_method1` (`id_method`),
  KEY `id_role1` (`id_role`),
  KEY `id_group1` (`id_group`),
  CONSTRAINT `id_group1` FOREIGN KEY (`id_group`) REFERENCES `groups` (`id`) ON UPDATE CASCADE,
  CONSTRAINT `id_method1` FOREIGN KEY (`id_method`) REFERENCES `method` (`id`) ON UPDATE CASCADE,
  CONSTRAINT `id_role1` FOREIGN KEY (`id_role`) REFERENCES `role` (`id`) ON UPDATE CASCADE,
  CONSTRAINT `id_spec1` FOREIGN KEY (`id_spec`) REFERENCES `spec` (`id`) ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=126 DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `user`
--

LOCK TABLES `user` WRITE;
/*!40000 ALTER TABLE `user` DISABLE KEYS */;
INSERT INTO `user` VALUE (4,2,1,3,2,'Администратор','admin','$5$rounds=100565$Pcd75/6kkOH.rc1K$n39OxB91GQxPPLxcYvH9qmbKpHOSS9LBt5Z0T5VXT6C');
/*!40000 ALTER TABLE `user` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2015-01-19 10:59:20
