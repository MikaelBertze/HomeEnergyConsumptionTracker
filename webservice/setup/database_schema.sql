--
-- Table structure for table `measurements`
--

DROP TABLE IF EXISTS `measurements`;
CREATE TABLE `measurements` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `sensor_id` int(11) NOT NULL,
  `sensor_type` varchar(20) NOT NULL,
  `date_time` datetime NOT NULL,
  `sensor_value` float NOT NULL,
  PRIMARY KEY (`id`),
  KEY `tick` (`date_time`)
) ENGINE=InnoDB AUTO_INCREMENT=0 DEFAULT CHARSET=latin1;
