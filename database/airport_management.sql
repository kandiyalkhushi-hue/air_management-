-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1:3307
-- Generation Time: Nov 14, 2026 at 08:19 AM
-- Server version: 10.4.32-MariaDB
-- PHP Version: 8.2.12

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `airport_management`
--

-- --------------------------------------------------------

--
-- Table structure for table `aircraft`
--

CREATE TABLE `aircraft` (
  `aircraft_id` int(11) NOT NULL,
  `airline_id` int(11) NOT NULL,
  `registration_number` varchar(30) NOT NULL,
  `model` varchar(100) NOT NULL,
  `aircraft_category` enum('LIGHT','MEDIUM','HEAVY') NOT NULL,
  `passenger_capacity` int(11) DEFAULT 0,
  `max_takeoff_weight` decimal(10,2) DEFAULT 0.00,
  `required_runway_type` enum('LIGHT','MEDIUM','HEAVY') NOT NULL,
  `status` enum('AVAILABLE','IN_FLIGHT','LANDED','PARKED','MAINTENANCE') DEFAULT 'AVAILABLE',
  `created_at` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `aircraft`
--

INSERT INTO `aircraft` (`aircraft_id`, `airline_id`, `registration_number`, `model`, `aircraft_category`, `passenger_capacity`, `max_takeoff_weight`, `required_runway_type`, `status`, `created_at`) VALUES
(1, 1, 'VT-ANB', 'Boeing 787', 'HEAVY', 256, 254000.00, 'HEAVY', 'AVAILABLE', '2026-10-07 14:22:37'),
(2, 2, 'VT-ABC', 'Airbus A320', 'MEDIUM', 186, 73500.00, 'MEDIUM', 'AVAILABLE', '2026-10-07 14:22:55');

-- --------------------------------------------------------

--
-- Table structure for table `airlines`
--

CREATE TABLE `airlines` (
  `airline_id` int(11) NOT NULL,
  `airline_code` varchar(10) NOT NULL,
  `airline_name` varchar(150) NOT NULL,
  `country` varchar(100) DEFAULT NULL,
  `status` enum('ACTIVE','INACTIVE') DEFAULT 'ACTIVE',
  `created_at` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `airlines`
--

INSERT INTO `airlines` (`airline_id`, `airline_code`, `airline_name`, `country`, `status`, `created_at`) VALUES
(1, 'AI', 'Air India', 'India', 'ACTIVE', '2026-10-07 14:15:44'),
(2, '6E', 'IndiGo', 'India', 'ACTIVE', '2026-10-07 14:16:11');

-- --------------------------------------------------------

--
-- Table structure for table `airports`
--

CREATE TABLE `airports` (
  `airport_id` int(11) NOT NULL,
  `airport_code` varchar(10) NOT NULL,
  `airport_name` varchar(150) NOT NULL,
  `city` varchar(100) NOT NULL,
  `country` varchar(100) NOT NULL,
  `timezone` varchar(50) DEFAULT 'IST',
  `max_aircraft_capacity` int(11) DEFAULT 0,
  `operating_hours` varchar(50) DEFAULT '24x7',
  `status` enum('ACTIVE','INACTIVE') DEFAULT 'ACTIVE',
  `created_at` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `airports`
--

INSERT INTO `airports` (`airport_id`, `airport_code`, `airport_name`, `city`, `country`, `timezone`, `max_aircraft_capacity`, `operating_hours`, `status`, `created_at`) VALUES
(25, 'MUM-001', 'Mumbai Intl airport', 'Mumbai', 'India', 'Asia/Kolkata', 100, '24 Hours', 'ACTIVE', '2026-10-15 15:03:45');

-- --------------------------------------------------------

--
-- Table structure for table `atc_controllers`
--

CREATE TABLE `atc_controllers` (
  `atc_id` int(11) NOT NULL,
  `airport_id` int(11) NOT NULL,
  `employee_code` varchar(30) NOT NULL,
  `controller_name` varchar(120) NOT NULL,
  `experience_years` int(11) DEFAULT 0,
  `shift` enum('MORNING','EVENING','NIGHT') NOT NULL,
  `status` enum('AVAILABLE','BUSY','ON_BREAK','OFF_DUTY') DEFAULT 'AVAILABLE',
  `max_concurrent_flights` int(11) DEFAULT 1,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `atc_controllers`
--

INSERT INTO `atc_controllers` (`atc_id`, `airport_id`, `employee_code`, `controller_name`, `experience_years`, `shift`, `status`, `max_concurrent_flights`, `created_at`) VALUES
(4, 25, 'ATC-001', 'Mayank', 3, 'MORNING', 'AVAILABLE', 5, '2026-10-15 15:05:59'),
(5, 25, 'ATC-002', 'Khushi', 3, 'EVENING', 'AVAILABLE', 5, '2026-10-15 15:06:16'),
(6, 25, 'ATC-003', 'Pooja', 3, 'NIGHT', 'AVAILABLE', 5, '2026-10-15 15:06:27');

-- --------------------------------------------------------

--
-- Table structure for table `flights`
--

CREATE TABLE `flights` (
  `flight_id` int(11) NOT NULL,
  `flight_number` varchar(20) NOT NULL,
  `airline_id` int(11) NOT NULL,
  `aircraft_id` int(11) NOT NULL,
  `airport_id` int(11) NOT NULL,
  `terminal_id` int(11) DEFAULT NULL,
  `gate_id` int(11) DEFAULT NULL,
  `operation_type` enum('ARRIVAL','DEPARTURE') NOT NULL,
  `arrival_time` datetime DEFAULT NULL,
  `departure_time` datetime DEFAULT NULL,
  `processing_time_minutes` int(11) NOT NULL DEFAULT 5,
  `priority` int(11) NOT NULL DEFAULT 5,
  `current_situation` enum('NORMAL','EMERGENCY','LOW_FUEL','MEDICAL','WEATHER','VIP') NOT NULL DEFAULT 'NORMAL',
  `fuel_percentage` decimal(5,2) DEFAULT 100.00,
  `passenger_count` int(11) DEFAULT 0,
  `is_emergency` tinyint(1) DEFAULT 0,
  `emergency_reason` varchar(255) DEFAULT NULL,
  `status` enum('SCHEDULED','WAITING','BOARDING','TAXIING','LANDING','TAKEOFF','COMPLETED','DELAYED','CANCELLED','EMERGENCY') DEFAULT 'WAITING',
  `created_at` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `flights`
--

INSERT INTO `flights` (`flight_id`, `flight_number`, `airline_id`, `aircraft_id`, `airport_id`, `terminal_id`, `gate_id`, `operation_type`, `arrival_time`, `departure_time`, `processing_time_minutes`, `priority`, `current_situation`, `fuel_percentage`, `passenger_count`, `is_emergency`, `emergency_reason`, `status`, `created_at`) VALUES
(22, 'pbl105', 1, 1, 25, 3, 2, 'ARRIVAL', '2026-11-16 06:33:00', NULL, 8, 5, 'NORMAL', 69.00, 155, 1, '', 'SCHEDULED', '2026-11-13 17:32:55'),
(23, 'pbl104', 1, 1, 25, 3, 2, 'ARRIVAL', '2026-11-16 06:34:00', NULL, 3, 5, 'NORMAL', 55.00, NULL, 0, '', 'SCHEDULED', '2026-11-13 17:33:37'),
(24, 'pbl103', 1, 1, 25, 3, 2, 'ARRIVAL', '2026-11-16 06:32:00', NULL, 6, 5, 'VIP', 99.00, 200, 0, '', 'SCHEDULED', '2026-11-13 17:34:50'),
(25, 'pbl1099', 1, 1, 25, 3, 2, 'ARRIVAL', '2026-11-16 06:32:00', NULL, 4, 5, 'MEDICAL', 80.00, NULL, 0, '', 'WAITING', '2026-11-13 17:35:49'),
(26, 'pbl1088', 1, 1, 25, 3, 2, 'ARRIVAL', '2026-11-16 06:32:00', NULL, 2, 5, 'NORMAL', 80.00, NULL, 0, '', 'WAITING', '2026-11-13 17:36:40');

-- --------------------------------------------------------

--
-- Table structure for table `gates`
--

CREATE TABLE `gates` (
  `gate_id` int(11) NOT NULL,
  `terminal_id` int(11) NOT NULL,
  `gate_number` varchar(20) NOT NULL,
  `gate_type` enum('DOMESTIC','INTERNATIONAL','MIXED') DEFAULT 'MIXED',
  `status` enum('AVAILABLE','OCCUPIED','BOARDING','CLOSED','MAINTENANCE') DEFAULT 'AVAILABLE',
  `created_at` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `gates`
--

INSERT INTO `gates` (`gate_id`, `terminal_id`, `gate_number`, `gate_type`, `status`, `created_at`) VALUES
(2, 3, 'G-01', 'DOMESTIC', 'AVAILABLE', '2026-10-15 15:04:41'),
(3, 3, 'G-02', 'DOMESTIC', 'AVAILABLE', '2026-10-15 15:04:52'),
(4, 4, 'G-01', 'DOMESTIC', 'AVAILABLE', '2026-10-15 15:05:02'),
(5, 4, 'G-02', '', 'AVAILABLE', '2026-10-15 15:05:19');

-- --------------------------------------------------------

--
-- Table structure for table `runways`
--

CREATE TABLE `runways` (
  `runway_id` int(11) NOT NULL,
  `airport_id` int(11) NOT NULL,
  `runway_code` varchar(20) NOT NULL,
  `length_meters` int(11) NOT NULL,
  `width_meters` int(11) NOT NULL,
  `runway_type` enum('LIGHT','MEDIUM','HEAVY') NOT NULL,
  `allowed_operation` enum('LANDING','TAKEOFF','BOTH') DEFAULT 'BOTH',
  `ils_available` tinyint(1) DEFAULT 0,
  `night_operation` tinyint(1) DEFAULT 1,
  `status` enum('AVAILABLE','OCCUPIED','CLOSED','MAINTENANCE','RESTRICTED') DEFAULT 'AVAILABLE',
  `created_at` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `runways`
--

INSERT INTO `runways` (`runway_id`, `airport_id`, `runway_code`, `length_meters`, `width_meters`, `runway_type`, `allowed_operation`, `ils_available`, `night_operation`, `status`, `created_at`) VALUES
(4, 25, '12001', 7622, 1212, 'MEDIUM', 'BOTH', 1, 1, 'AVAILABLE', '2026-10-15 15:05:30'),
(6, 25, '122001', 34, 37, 'MEDIUM', 'BOTH', 1, 1, 'AVAILABLE', '2026-10-15 15:25:17'),
(7, 25, '1222', 866, 666, 'HEAVY', 'BOTH', 1, 1, 'AVAILABLE', '2026-11-13 17:51:11'),
(8, 25, '6000', 500, 566, 'LIGHT', 'BOTH', 1, 1, 'AVAILABLE', '2026-11-13 18:14:22'),
(9, 25, '18888', 600, 599, 'HEAVY', 'BOTH', 1, 1, 'AVAILABLE', '2026-11-13 19:18:40');

-- --------------------------------------------------------

--
-- Table structure for table `scheduler_runs`
--

CREATE TABLE `scheduler_runs` (
  `run_id` int(11) NOT NULL,
  `algorithm` enum('FCFS','SJF','SRTF','PRIORITY','ROUND_ROBIN','HRRN','MLQ','MLFQ') NOT NULL,
  `started_at` datetime DEFAULT current_timestamp(),
  `completed_at` datetime DEFAULT NULL,
  `status` enum('RUNNING','COMPLETED','FAILED') DEFAULT 'RUNNING',
  `total_flights` int(11) DEFAULT 0,
  `average_waiting_time` decimal(10,2) DEFAULT 0.00,
  `average_turnaround_time` decimal(10,2) DEFAULT 0.00,
  `average_response_time` decimal(10,2) DEFAULT 0.00,
  `throughput` decimal(10,2) DEFAULT 0.00,
  `runway_utilization` decimal(10,2) DEFAULT 0.00,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `scheduler_runs`
--

INSERT INTO `scheduler_runs` (`run_id`, `algorithm`, `started_at`, `completed_at`, `status`, `total_flights`, `average_waiting_time`, `average_turnaround_time`, `average_response_time`, `throughput`, `runway_utilization`, `created_at`) VALUES
(1, 'PRIORITY', '2026-10-07 20:39:48', NULL, 'RUNNING', 1, 0.00, 0.00, 0.00, 0.00, 0.00, '2026-10-07 15:09:48'),
(2, 'PRIORITY', '2026-10-07 20:43:40', '2026-10-07 20:43:40', 'COMPLETED', 1, 0.00, 0.00, 0.00, 0.00, 0.00, '2026-10-07 15:13:40'),
(3, 'FCFS', '2026-10-07 21:41:18', '2026-10-07 21:41:18', 'FAILED', 1, 0.00, 10.00, 0.00, 0.10, 100.00, '2026-10-07 16:11:18'),
(4, 'SRTF', '2026-10-08 19:44:09', '2026-10-08 19:44:09', 'FAILED', 1, 0.00, 10.00, 0.00, 0.10, 100.00, '2026-10-08 14:14:09'),
(5, 'PRIORITY', '2026-10-08 19:44:27', '2026-10-08 19:44:27', 'FAILED', 1, 0.00, 0.00, 0.00, 0.00, 0.00, '2026-10-08 14:14:27'),
(6, 'FCFS', '2026-10-08 19:44:40', '2026-10-08 19:44:40', 'FAILED', 1, 0.00, 10.00, 0.00, 0.10, 100.00, '2026-10-08 14:14:40'),
(7, 'FCFS', '2026-10-08 19:49:15', '2026-10-08 19:49:15', 'FAILED', 1, 0.00, 10.00, 0.00, 0.10, 100.00, '2026-10-08 14:19:15'),
(8, 'FCFS', '2026-10-08 20:03:39', '2026-10-08 20:03:39', 'COMPLETED', 2, 0.00, 10.00, 0.00, 0.00, 0.11, '2026-10-08 14:33:39'),
(9, 'ROUND_ROBIN', '2026-10-08 20:04:04', '2026-10-08 20:04:04', 'FAILED', 1, 0.00, 10.00, 0.00, 0.10, 100.00, '2026-10-08 14:34:04'),
(10, 'SJF', '2026-10-08 20:04:13', '2026-10-08 20:04:13', 'FAILED', 1, 0.00, 10.00, 0.00, 0.10, 100.00, '2026-10-08 14:34:13'),
(11, 'FCFS', '2026-10-08 20:06:56', '2026-10-08 20:06:56', 'COMPLETED', 2, 0.00, 10.00, 0.00, 0.00, 0.70, '2026-10-08 14:36:56'),
(12, 'SRTF', '2026-10-08 20:07:34', '2026-10-08 20:07:34', 'FAILED', 1, 0.00, 10.00, 0.00, 0.10, 100.00, '2026-10-08 14:37:34'),
(13, 'MLQ', '2026-10-08 20:07:41', '2026-10-08 20:07:41', 'FAILED', 1, 0.00, 10.00, 0.00, 0.10, 100.00, '2026-10-08 14:37:41'),
(14, 'FCFS', '2026-10-08 20:07:45', '2026-10-08 20:07:45', 'FAILED', 1, 0.00, 10.00, 0.00, 0.10, 100.00, '2026-10-08 14:37:45'),
(15, 'FCFS', '2026-10-08 20:08:03', '2026-10-08 20:08:03', 'FAILED', 1, 0.00, 10.00, 0.00, 0.10, 100.00, '2026-10-08 14:38:03'),
(16, 'FCFS', '2026-10-14 19:55:39', '2026-10-14 19:55:39', 'FAILED', 1, 0.00, 10.00, 0.00, 0.10, 100.00, '2026-10-14 14:25:39'),
(17, 'SJF', '2026-10-14 19:56:06', '2026-10-14 19:56:06', 'FAILED', 1, 0.00, 10.00, 0.00, 0.10, 100.00, '2026-10-14 14:26:06'),
(18, 'FCFS', '2026-10-14 19:56:14', '2026-10-14 19:56:14', 'FAILED', 1, 0.00, 10.00, 0.00, 0.10, 100.00, '2026-10-14 14:26:14'),
(19, 'ROUND_ROBIN', '2026-10-14 19:56:25', '2026-10-14 19:56:25', 'FAILED', 1, 0.00, 10.00, 0.00, 0.10, 100.00, '2026-10-14 14:26:25'),
(20, 'SRTF', '2026-10-14 19:58:55', '2026-10-14 19:58:55', 'FAILED', 1, 0.00, 8.00, 0.00, 0.13, 100.00, '2026-10-14 14:28:55'),
(21, 'FCFS', '2026-10-15 19:59:48', '2026-10-15 19:59:48', 'FAILED', 5, 0.00, 43.40, 0.00, 0.00, 1.85, '2026-10-15 14:29:48'),
(22, 'SJF', '2026-10-15 20:00:07', '2026-10-15 20:00:07', 'FAILED', 5, 0.00, 43.40, 0.00, 0.00, 1.85, '2026-10-15 14:30:07'),
(23, 'PRIORITY', '2026-10-15 20:00:20', '2026-10-15 20:00:20', 'FAILED', 5, 0.00, 0.00, 0.00, 0.00, 0.00, '2026-10-15 14:30:20'),
(24, 'ROUND_ROBIN', '2026-10-15 20:00:26', '2026-10-15 20:00:26', 'FAILED', 5, 0.00, 43.40, 0.00, 0.00, 1.85, '2026-10-15 14:30:26'),
(25, 'ROUND_ROBIN', '2026-10-15 20:03:54', '2026-10-15 20:03:54', 'FAILED', 5, 0.00, 43.40, 0.00, 0.00, 1.85, '2026-10-15 14:33:54'),
(26, 'ROUND_ROBIN', '2026-10-15 20:04:03', '2026-10-15 20:04:03', 'FAILED', 5, 0.00, 43.40, 0.00, 0.00, 1.85, '2026-10-15 14:34:03'),
(27, 'ROUND_ROBIN', '2026-10-15 20:09:41', '2026-10-15 20:09:41', 'FAILED', 5, 0.00, 43.40, 0.00, 0.00, 1.85, '2026-10-15 14:39:41'),
(28, 'ROUND_ROBIN', '2026-10-15 20:11:17', '2026-10-15 20:11:18', 'FAILED', 5, 0.00, 43.40, 0.00, 0.00, 1.85, '2026-10-15 14:41:17'),
(29, 'FCFS', '2026-10-15 20:30:01', '2026-10-15 20:30:01', 'FAILED', 5, 0.00, 43.40, 0.00, 0.00, 1.85, '2026-10-15 15:00:01'),
(30, 'ROUND_ROBIN', '2026-10-15 20:30:19', '2026-10-15 20:30:19', 'FAILED', 5, 0.00, 43.40, 0.00, 0.00, 1.85, '2026-10-15 15:00:19'),
(31, 'ROUND_ROBIN', '2026-10-15 20:30:27', '2026-10-15 20:30:27', 'FAILED', 5, 0.00, 43.40, 0.00, 0.00, 1.85, '2026-10-15 15:00:27'),
(32, 'FCFS', '2026-10-15 20:31:34', '2026-10-15 20:31:34', 'COMPLETED', 5, 0.00, 43.40, 0.00, 0.00, 1.85, '2026-10-15 15:01:34'),
(33, 'FCFS', '2026-10-15 20:32:40', '2026-10-15 20:32:40', 'FAILED', 1, 0.00, 10.00, 0.00, 0.10, 100.00, '2026-10-15 15:02:40'),
(34, 'FCFS', '2026-10-15 20:39:09', '2026-10-15 20:39:09', 'FAILED', 2, 0.00, 6.50, 0.00, 0.00, 0.13, '2026-10-15 15:09:09'),
(35, 'SJF', '2026-10-15 20:40:05', '2026-10-15 20:40:05', 'FAILED', 2, 0.00, 6.50, 0.00, 0.00, 0.13, '2026-10-15 15:10:05'),
(36, 'PRIORITY', '2026-10-15 20:40:09', '2026-10-15 20:40:09', 'FAILED', 2, 0.00, 0.00, 0.00, 0.00, 0.00, '2026-10-15 15:10:09'),
(37, 'ROUND_ROBIN', '2026-10-15 20:40:17', '2026-10-15 20:40:17', 'FAILED', 2, 0.00, 6.50, 0.00, 0.00, 0.13, '2026-10-15 15:10:17'),
(38, 'FCFS', '2026-10-15 20:50:21', '2026-10-15 20:50:21', 'FAILED', 2, 0.00, 6.50, 0.00, 0.00, 0.13, '2026-10-15 15:20:21'),
(39, 'FCFS', '2026-10-15 20:50:35', '2026-10-15 20:50:35', 'FAILED', 2, 0.00, 6.50, 0.00, 0.00, 0.13, '2026-10-15 15:20:35'),
(40, 'FCFS', '2026-10-15 20:51:12', '2026-10-15 20:51:12', 'FAILED', 2, 0.00, 6.50, 0.00, 0.00, 0.13, '2026-10-15 15:21:12'),
(41, 'FCFS', '2026-10-15 20:51:46', '2026-10-15 20:51:46', 'COMPLETED', 2, 0.00, 6.50, 0.00, 0.00, 0.13, '2026-10-15 15:21:46'),
(42, 'FCFS', '2026-10-15 20:52:11', '2026-10-15 20:52:11', 'FAILED', 1, 0.00, 10.00, 0.00, 0.10, 100.00, '2026-10-15 15:22:11'),
(43, 'FCFS', '2026-10-15 20:52:38', '2026-10-15 20:52:38', 'FAILED', 1, 0.00, 10.00, 0.00, 0.10, 100.00, '2026-10-15 15:22:38'),
(44, 'SJF', '2026-10-15 20:53:00', '2026-10-15 20:53:00', 'FAILED', 1, 0.00, 10.00, 0.00, 0.10, 100.00, '2026-10-15 15:23:00'),
(45, 'FCFS', '2026-10-15 20:53:04', '2026-10-15 20:53:04', 'FAILED', 1, 0.00, 10.00, 0.00, 0.10, 100.00, '2026-10-15 15:23:04'),
(46, 'FCFS', '2026-10-15 20:54:07', '2026-10-15 20:54:07', 'FAILED', 1, 0.00, 10.00, 0.00, 0.10, 100.00, '2026-10-15 15:24:07'),
(47, 'FCFS', '2026-10-15 20:55:22', '2026-10-15 20:55:22', 'FAILED', 1, 0.00, 10.00, 0.00, 0.10, 100.00, '2026-10-15 15:25:22'),
(48, 'SJF', '2026-10-15 20:55:26', '2026-10-15 20:55:26', 'FAILED', 1, 0.00, 10.00, 0.00, 0.10, 100.00, '2026-10-15 15:25:26'),
(49, 'PRIORITY', '2026-10-15 20:56:48', '2026-10-15 20:56:48', 'FAILED', 1, 0.00, 0.00, 0.00, 0.00, 0.00, '2026-10-15 15:26:48'),
(50, 'PRIORITY', '2026-11-13 22:27:29', '2026-11-13 22:27:29', 'FAILED', 2, 0.00, 0.00, 0.00, 0.00, 0.00, '2026-11-13 16:57:29'),
(51, 'PRIORITY', '2026-11-13 22:36:51', '2026-11-13 22:36:51', 'FAILED', 2, 0.00, 0.00, 0.00, 0.00, 0.00, '2026-11-13 17:06:51'),
(52, 'SJF', '2026-11-13 23:06:53', '2026-11-13 23:06:53', 'FAILED', 5, 3.60, 9.20, 3.60, 0.00, 2.72, '2026-11-13 17:36:53'),
(53, 'FCFS', '2026-11-13 23:07:28', '2026-11-13 23:07:28', 'FAILED', 5, 5.00, 10.60, 5.00, 0.00, 2.72, '2026-11-13 17:37:28'),
(54, 'FCFS', '2026-11-13 23:21:19', '2026-11-13 23:21:19', 'COMPLETED', 5, 5.00, 10.60, 5.00, 0.00, 2.72, '2026-11-13 17:51:19'),
(55, 'SJF', '2026-11-13 23:23:50', '2026-11-13 23:23:50', 'FAILED', 4, 3.50, 8.50, 3.50, 0.20, 100.00, '2026-11-13 17:53:50'),
(56, 'PRIORITY', '2026-11-13 23:24:21', '2026-11-13 23:24:21', 'FAILED', 4, 0.00, 0.00, 0.00, 0.00, 0.00, '2026-11-13 17:54:21'),
(57, 'SJF', '2026-11-13 23:25:13', '2026-11-13 23:25:13', 'FAILED', 4, 3.50, 8.50, 3.50, 0.20, 100.00, '2026-11-13 17:55:13'),
(58, 'FCFS', '2026-11-13 23:25:57', '2026-11-13 23:25:57', 'FAILED', 5, 9.20, 14.80, 9.20, 0.18, 100.00, '2026-11-13 17:55:57'),
(59, 'SJF', '2026-11-13 23:39:23', '2026-11-13 23:39:23', 'FAILED', 5, 6.20, 11.80, 6.20, 0.18, 100.00, '2026-11-13 18:09:23'),
(60, 'PRIORITY', '2026-11-13 23:40:00', '2026-11-13 23:40:00', 'FAILED', 5, 12.00, 17.60, 12.00, 0.18, 100.00, '2026-11-13 18:10:00'),
(61, 'FCFS', '2026-11-13 23:41:15', '2026-11-13 23:41:15', 'FAILED', 5, 9.20, 14.80, 9.20, 0.18, 100.00, '2026-11-13 18:11:15'),
(62, 'SJF', '2026-11-13 23:42:08', '2026-11-13 23:42:08', 'FAILED', 5, 6.20, 11.80, 6.20, 0.18, 100.00, '2026-11-13 18:12:08'),
(63, 'SJF', '2026-11-13 23:45:20', '2026-11-13 23:45:20', 'FAILED', 5, 6.20, 11.80, 6.20, 0.18, 100.00, '2026-11-13 18:15:20'),
(64, 'SJF', '2026-11-13 23:53:01', '2026-11-13 23:53:01', 'FAILED', 5, 6.20, 11.80, 6.20, 0.18, 100.00, '2026-11-13 18:23:01'),
(65, 'SJF', '2026-11-13 23:56:17', '2026-11-13 23:56:17', 'COMPLETED', 5, 6.20, 11.80, 6.20, 0.18, 100.00, '2026-11-13 18:26:17'),
(66, 'FCFS', '2026-11-13 23:56:46', '2026-11-13 23:56:46', 'COMPLETED', 4, 4.75, 9.50, 4.75, 0.21, 100.00, '2026-11-13 18:26:46'),
(67, 'PRIORITY', '2026-11-13 23:57:14', '2026-11-13 23:57:14', 'COMPLETED', 3, 0.00, 3.67, 0.00, 0.21, 78.57, '2026-11-13 18:27:14'),
(68, 'SJF', '2026-11-13 23:58:33', '2026-11-13 23:58:33', 'COMPLETED', 5, 2.20, 6.80, 2.20, 0.01, 6.61, '2026-11-13 18:28:33'),
(69, 'SJF', '2026-11-13 23:58:47', '2026-11-13 23:58:47', 'FAILED', 2, 0.00, 2.50, 0.00, 0.29, 71.43, '2026-11-13 18:28:47'),
(70, 'SJF', '2026-11-13 23:58:53', '2026-11-13 23:58:53', 'FAILED', 2, 0.00, 2.50, 0.00, 0.29, 71.43, '2026-11-13 18:28:53'),
(71, 'PRIORITY', '2026-11-14 00:04:06', '2026-11-14 00:04:06', 'COMPLETED', 5, 4.00, 8.60, 4.00, 0.02, 7.44, '2026-11-13 18:34:06'),
(72, 'PRIORITY', '2026-11-14 00:04:37', '2026-11-14 00:04:37', 'FAILED', 4, 5.00, 8.75, 5.00, 0.27, 100.00, '2026-11-13 18:34:37'),
(73, 'FCFS', '2026-11-14 00:09:24', '2026-11-14 00:09:24', 'FAILED', 4, 3.25, 7.00, 3.25, 0.27, 100.00, '2026-11-13 18:39:24'),
(74, 'SJF', '2026-11-14 00:12:28', '2026-11-14 00:12:28', 'FAILED', 4, 2.50, 6.25, 2.50, 0.27, 100.00, '2026-11-13 18:42:28'),
(75, 'SJF', '2026-11-14 00:15:21', '2026-11-14 00:15:21', 'FAILED', 4, 2.50, 6.25, 2.50, 0.27, 100.00, '2026-11-13 18:45:21'),
(76, 'PRIORITY', '2026-11-14 00:29:21', '2026-11-14 00:29:21', 'COMPLETED', 4, 0.25, 4.00, 0.25, 0.00, 1.56, '2026-11-13 18:59:21'),
(77, 'FCFS', '2026-11-14 00:29:51', '2026-11-14 00:29:51', 'FAILED', 2, 0.50, 5.00, 0.50, 0.22, 100.00, '2026-11-13 18:59:51'),
(78, 'SJF', '2026-11-14 00:30:02', '2026-11-14 00:30:02', 'FAILED', 2, 0.50, 5.00, 0.50, 0.22, 100.00, '2026-11-13 19:00:02'),
(79, 'FCFS', '2026-11-14 00:30:20', '2026-11-14 00:30:20', 'FAILED', 2, 0.50, 5.00, 0.50, 0.22, 100.00, '2026-11-13 19:00:20'),
(80, 'MLQ', '2026-11-14 00:30:29', '2026-11-14 00:30:29', 'FAILED', 2, 4.00, 8.50, 4.00, 0.22, 100.00, '2026-11-13 19:00:29'),
(81, 'PRIORITY', '2026-11-14 00:31:12', '2026-11-14 00:31:12', 'FAILED', 2, 0.50, 5.00, 0.50, 0.22, 100.00, '2026-11-13 19:01:12'),
(82, 'SJF', '2026-11-14 00:31:47', '2026-11-14 00:31:47', 'FAILED', 2, 0.50, 5.00, 0.50, 0.22, 100.00, '2026-11-13 19:01:47'),
(83, 'FCFS', '2026-11-14 00:32:06', '2026-11-14 00:32:06', 'FAILED', 2, 0.50, 5.00, 0.50, 0.22, 100.00, '2026-11-13 19:02:06'),
(84, 'FCFS', '2026-11-14 00:32:45', '2026-11-14 00:32:45', 'FAILED', 2, 0.50, 5.00, 0.50, 0.22, 100.00, '2026-11-13 19:02:45'),
(85, 'SJF', '2026-11-14 00:34:04', '2026-11-14 00:34:04', 'FAILED', 2, 0.50, 5.00, 0.50, 0.22, 100.00, '2026-11-13 19:04:04'),
(86, 'PRIORITY', '2026-11-14 00:34:20', '2026-11-14 00:34:20', 'FAILED', 2, 0.50, 5.00, 0.50, 0.22, 100.00, '2026-11-13 19:04:20'),
(87, 'FCFS', '2026-11-14 00:34:45', '2026-11-14 00:34:45', 'FAILED', 2, 0.50, 5.00, 0.50, 0.22, 100.00, '2026-11-13 19:04:45'),
(88, 'SJF', '2026-11-14 00:36:01', '2026-11-14 00:36:01', 'FAILED', 2, 0.50, 5.00, 0.50, 0.22, 100.00, '2026-11-13 19:06:01'),
(89, 'PRIORITY', '2026-11-14 00:37:32', '2026-11-14 00:37:32', 'FAILED', 2, 0.50, 5.00, 0.50, 0.22, 100.00, '2026-11-13 19:07:32'),
(90, 'FCFS', '2026-11-14 00:38:08', '2026-11-14 00:38:08', 'FAILED', 2, 0.50, 5.00, 0.50, 0.22, 100.00, '2026-11-13 19:08:08'),
(91, 'FCFS', '2026-11-14 00:38:54', '2026-11-14 00:38:54', 'FAILED', 2, 0.50, 5.00, 0.50, 0.22, 100.00, '2026-11-13 19:08:54'),
(92, 'FCFS', '2026-11-14 00:40:49', '2026-11-14 00:40:49', 'FAILED', 2, 0.50, 5.00, 0.50, 0.22, 100.00, '2026-11-13 19:10:49'),
(93, 'PRIORITY', '2026-11-14 00:41:06', '2026-11-14 00:41:06', 'FAILED', 2, 0.50, 5.00, 0.50, 0.22, 100.00, '2026-11-13 19:11:06'),
(94, 'PRIORITY', '2026-11-14 00:41:42', '2026-11-14 00:41:42', 'COMPLETED', 5, 0.20, 4.80, 0.20, 0.01, 2.39, '2026-11-13 19:11:42'),
(95, 'PRIORITY', '2026-11-14 00:42:29', '2026-11-14 00:42:29', 'FAILED', 2, 0.50, 5.00, 0.50, 0.22, 100.00, '2026-11-13 19:12:29'),
(96, 'PRIORITY', '2026-11-14 00:44:13', '2026-11-14 00:44:13', 'COMPLETED', 4, 0.25, 4.00, 0.25, 0.00, 1.56, '2026-11-13 19:14:13'),
(97, 'FCFS', '2026-11-14 00:47:32', '2026-11-14 00:47:32', 'FAILED', 2, 0.50, 5.00, 0.50, 0.22, 100.00, '2026-11-13 19:17:32'),
(98, 'PRIORITY', '2026-11-14 00:48:47', '2026-11-14 00:48:47', 'COMPLETED', 2, 0.50, 5.00, 0.50, 0.22, 100.00, '2026-11-13 19:18:47'),
(99, 'PRIORITY', '2026-11-14 00:49:57', '2026-11-14 00:49:57', 'COMPLETED', 5, 0.20, 4.80, 0.20, 0.01, 2.39, '2026-11-13 19:19:57'),
(100, 'PRIORITY', '2026-11-14 00:52:17', '2026-11-14 00:52:17', 'COMPLETED', 2, 0.00, 3.00, 0.00, 0.00, 0.62, '2026-11-13 19:22:17'),
(101, 'PRIORITY', '2026-11-14 00:53:38', '2026-11-14 00:53:38', 'COMPLETED', 2, 2.00, 7.00, 2.00, 0.20, 100.00, '2026-11-13 19:23:38'),
(102, 'PRIORITY', '2026-11-14 00:57:05', '2026-11-14 00:57:06', 'COMPLETED', 2, 0.00, 3.00, 0.00, 0.01, 2.01, '2026-11-13 19:27:05'),
(103, 'SJF', '2026-11-14 00:58:19', '2026-11-14 00:58:19', 'COMPLETED', 2, 0.00, 3.00, 0.00, 0.01, 2.01, '2026-11-13 19:28:19'),
(104, 'SJF', '2026-11-14 01:00:23', '2026-11-14 01:00:23', 'COMPLETED', 2, 0.00, 3.00, 0.00, 0.01, 2.01, '2026-11-13 19:30:23'),
(105, 'PRIORITY', '2026-11-14 01:05:27', '2026-11-14 01:05:27', 'COMPLETED', 5, 8.80, 13.40, 8.80, 0.22, 100.00, '2026-11-13 19:35:27'),
(106, 'PRIORITY', '2026-11-14 12:43:32', '2026-11-14 12:43:32', 'COMPLETED', 2, 0.50, 3.50, 0.50, 0.33, 100.00, '2026-11-14 07:13:32'),
(107, 'PRIORITY', '2026-11-14 12:45:27', '2026-11-14 12:45:27', 'FAILED', 2, 2.00, 5.00, 2.00, 0.33, 100.00, '2026-11-14 07:15:27');

-- --------------------------------------------------------

--
-- Table structure for table `schedules`
--

CREATE TABLE `schedules` (
  `schedule_id` int(11) NOT NULL,
  `run_id` int(11) DEFAULT NULL,
  `flight_id` int(11) NOT NULL,
  `runway_id` int(11) NOT NULL,
  `atc_id` int(11) DEFAULT NULL,
  `algorithm` enum('FCFS','SJF','SRTF','PRIORITY','ROUND_ROBIN','HRRN','MLQ','MLFQ') NOT NULL,
  `situation` enum('NORMAL','EMERGENCY','LOW_FUEL','MEDICAL','WEATHER','VIP') NOT NULL DEFAULT 'NORMAL',
  `queue_position` int(11) DEFAULT 0,
  `scheduled_start` datetime DEFAULT NULL,
  `scheduled_end` datetime DEFAULT NULL,
  `waiting_time_minutes` int(11) DEFAULT 0,
  `turnaround_time_minutes` int(11) DEFAULT 0,
  `response_time_minutes` int(11) DEFAULT 0,
  `status` enum('SCHEDULED','IN_PROGRESS','COMPLETED','CANCELLED') DEFAULT 'SCHEDULED',
  `created_at` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `schedules`
--

INSERT INTO `schedules` (`schedule_id`, `run_id`, `flight_id`, `runway_id`, `atc_id`, `algorithm`, `situation`, `queue_position`, `scheduled_start`, `scheduled_end`, `waiting_time_minutes`, `turnaround_time_minutes`, `response_time_minutes`, `status`, `created_at`) VALUES
(10, 54, 22, 7, 4, 'FCFS', 'NORMAL', 1, '2026-11-16 06:00:00', '2026-11-16 06:08:00', 0, 8, 0, 'SCHEDULED', '2026-11-13 17:51:19'),
(11, 54, 24, 7, 4, 'FCFS', 'VIP', 2, '2026-11-16 06:08:00', '2026-11-16 06:14:00', 8, 14, 8, 'SCHEDULED', '2026-11-13 17:51:19'),
(12, 54, 23, 7, 4, 'FCFS', 'NORMAL', 3, '2026-11-16 06:14:00', '2026-11-16 06:17:00', 10, 13, 10, 'SCHEDULED', '2026-11-13 17:51:19'),
(13, 54, 25, 7, 4, 'FCFS', 'MEDICAL', 4, '2026-11-16 06:17:00', '2026-11-16 06:26:00', 7, 16, 7, 'SCHEDULED', '2026-11-13 17:51:19'),
(14, 54, 26, 7, 4, 'FCFS', 'NORMAL', 5, '2026-11-16 23:06:00', '2026-11-16 23:08:00', 0, 2, 0, 'SCHEDULED', '2026-11-13 17:51:19'),
(15, 65, 25, 7, 4, 'SJF', 'MEDICAL', 5, '2026-11-16 06:19:00', '2026-11-16 06:28:00', 18, 27, 18, 'SCHEDULED', '2026-11-13 18:26:17'),
(16, 66, 22, 7, 4, 'FCFS', 'NORMAL', 1, '2026-11-16 06:00:00', '2026-11-16 06:08:00', 0, 8, 0, 'SCHEDULED', '2026-11-13 18:26:46'),
(17, 67, 24, 7, 4, 'PRIORITY', 'VIP', 3, '2026-11-16 06:08:00', '2026-11-16 06:14:00', 0, 6, 0, 'SCHEDULED', '2026-11-13 18:27:14'),
(18, 68, 22, 7, 4, 'SJF', 'NORMAL', 3, '2026-11-16 11:30:00', '2026-11-16 11:38:00', 0, 8, 0, 'SCHEDULED', '2026-11-13 18:28:33'),
(19, 68, 25, 7, 4, 'SJF', 'MEDICAL', 4, '2026-11-16 11:38:00', '2026-11-16 11:42:00', 7, 11, 7, 'SCHEDULED', '2026-11-13 18:28:33'),
(20, 68, 24, 7, 4, 'SJF', 'VIP', 5, '2026-11-16 11:42:00', '2026-11-16 11:48:00', 4, 10, 4, 'SCHEDULED', '2026-11-13 18:28:33'),
(21, 71, 22, 7, 4, 'PRIORITY', 'NORMAL', 5, '2026-11-16 16:33:00', '2026-11-16 16:41:00', 0, 8, 0, 'SCHEDULED', '2026-11-13 18:34:06'),
(22, 76, 26, 7, 4, 'PRIORITY', 'NORMAL', 1, '2026-11-16 06:32:00', '2026-11-16 06:34:00', 0, 2, 0, 'SCHEDULED', '2026-11-13 18:59:21'),
(23, 76, 25, 7, 4, 'PRIORITY', 'MEDICAL', 4, '2026-11-16 22:32:00', '2026-11-16 22:36:00', 0, 4, 0, 'SCHEDULED', '2026-11-13 18:59:21'),
(24, 94, 26, 7, 4, 'PRIORITY', 'NORMAL', 1, '2026-11-16 06:32:00', '2026-11-16 06:34:00', 0, 2, 0, 'SCHEDULED', '2026-11-13 19:11:42'),
(25, 94, 22, 7, 4, 'PRIORITY', 'NORMAL', 4, '2026-11-16 16:33:00', '2026-11-16 16:41:00', 0, 8, 0, 'SCHEDULED', '2026-11-13 19:11:42'),
(26, 94, 25, 7, 4, 'PRIORITY', 'MEDICAL', 5, '2026-11-16 22:32:00', '2026-11-16 22:36:00', 0, 4, 0, 'SCHEDULED', '2026-11-13 19:11:42'),
(27, 96, 26, 7, 4, 'PRIORITY', 'NORMAL', 1, '2026-11-16 06:32:00', '2026-11-16 06:34:00', 0, 2, 0, 'SCHEDULED', '2026-11-13 19:14:13'),
(28, 96, 25, 7, 4, 'PRIORITY', 'MEDICAL', 4, '2026-11-16 22:32:00', '2026-11-16 22:36:00', 0, 4, 0, 'SCHEDULED', '2026-11-13 19:14:13'),
(29, 98, 23, 9, 4, 'PRIORITY', 'NORMAL', 1, '2026-11-16 11:34:00', '2026-11-16 11:37:00', 0, 3, 0, 'SCHEDULED', '2026-11-13 19:18:47'),
(30, 98, 24, 9, 4, 'PRIORITY', 'VIP', 2, '2026-11-16 11:37:00', '2026-11-16 11:43:00', 1, 7, 1, 'SCHEDULED', '2026-11-13 19:18:47'),
(31, 99, 26, 7, 4, 'PRIORITY', 'NORMAL', 1, '2026-11-16 06:32:00', '2026-11-16 06:34:00', 0, 2, 0, 'SCHEDULED', '2026-11-13 19:19:57'),
(32, 99, 23, 9, 4, 'PRIORITY', 'NORMAL', 2, '2026-11-16 11:34:00', '2026-11-16 11:37:00', 0, 3, 0, 'SCHEDULED', '2026-11-13 19:19:57'),
(33, 99, 24, 9, 4, 'PRIORITY', 'VIP', 3, '2026-11-16 11:37:00', '2026-11-16 11:43:00', 1, 7, 1, 'SCHEDULED', '2026-11-13 19:19:57'),
(34, 99, 22, 7, 4, 'PRIORITY', 'NORMAL', 4, '2026-11-16 16:33:00', '2026-11-16 16:41:00', 0, 8, 0, 'SCHEDULED', '2026-11-13 19:19:57'),
(35, 99, 25, 7, 4, 'PRIORITY', 'MEDICAL', 5, '2026-11-16 22:32:00', '2026-11-16 22:36:00', 0, 4, 0, 'SCHEDULED', '2026-11-13 19:19:57'),
(36, 100, 26, 7, 4, 'PRIORITY', 'NORMAL', 1, '2026-11-16 06:32:00', '2026-11-16 06:34:00', 0, 2, 0, 'SCHEDULED', '2026-11-13 19:22:17'),
(37, 100, 25, 7, 4, 'PRIORITY', 'MEDICAL', 2, '2026-11-16 22:32:00', '2026-11-16 22:36:00', 0, 4, 0, 'SCHEDULED', '2026-11-13 19:22:17'),
(38, 101, 25, 7, 4, 'PRIORITY', 'MEDICAL', 1, '2026-11-16 01:35:00', '2026-11-16 01:39:00', 0, 4, 0, 'SCHEDULED', '2026-11-13 19:23:38'),
(39, 101, 24, 7, 4, 'PRIORITY', 'VIP', 2, '2026-11-16 01:39:00', '2026-11-16 01:45:00', 4, 10, 4, 'SCHEDULED', '2026-11-13 19:23:38'),
(40, 102, 25, 7, 4, 'PRIORITY', 'MEDICAL', 1, '2026-11-16 01:35:00', '2026-11-16 01:39:00', 0, 4, 0, 'SCHEDULED', '2026-11-13 19:27:06'),
(41, 102, 26, 7, 5, 'PRIORITY', 'NORMAL', 2, '2026-11-16 06:32:00', '2026-11-16 06:34:00', 0, 2, 0, 'SCHEDULED', '2026-11-13 19:27:06'),
(42, 103, 25, 7, 4, 'SJF', 'MEDICAL', 1, '2026-11-16 01:35:00', '2026-11-16 01:39:00', 0, 4, 0, 'SCHEDULED', '2026-11-13 19:28:19'),
(43, 103, 26, 7, 5, 'SJF', 'NORMAL', 2, '2026-11-16 06:32:00', '2026-11-16 06:34:00', 0, 2, 0, 'SCHEDULED', '2026-11-13 19:28:19'),
(44, 104, 25, 7, 4, 'SJF', 'MEDICAL', 1, '2026-11-16 01:35:00', '2026-11-16 01:39:00', 0, 4, 0, 'SCHEDULED', '2026-11-13 19:30:23'),
(45, 104, 26, 7, 5, 'SJF', 'NORMAL', 2, '2026-11-16 06:32:00', '2026-11-16 06:34:00', 0, 2, 0, 'SCHEDULED', '2026-11-13 19:30:23'),
(46, 105, 24, 9, 5, 'PRIORITY', 'VIP', 1, '2026-11-16 06:32:00', '2026-11-16 06:38:00', 0, 6, 0, 'SCHEDULED', '2026-11-13 19:35:27'),
(47, 105, 25, 7, 4, 'PRIORITY', 'MEDICAL', 2, '2026-11-16 06:38:00', '2026-11-16 06:42:00', 5, 9, 5, 'SCHEDULED', '2026-11-13 19:35:27'),
(48, 105, 26, 7, 4, 'PRIORITY', 'NORMAL', 3, '2026-11-16 06:42:00', '2026-11-16 06:44:00', 10, 12, 10, 'SCHEDULED', '2026-11-13 19:35:27'),
(49, 105, 22, 7, 4, 'PRIORITY', 'NORMAL', 4, '2026-11-16 06:44:00', '2026-11-16 06:52:00', 11, 19, 11, 'SCHEDULED', '2026-11-13 19:35:27'),
(50, 105, 23, 7, 4, 'PRIORITY', 'NORMAL', 5, '2026-11-16 06:52:00', '2026-11-16 06:55:00', 18, 21, 18, 'SCHEDULED', '2026-11-13 19:35:27'),
(51, 106, 26, 7, 5, 'PRIORITY', 'NORMAL', 1, '2026-11-16 06:32:00', '2026-11-16 06:34:00', 0, 2, 0, 'SCHEDULED', '2026-11-14 07:13:32'),
(52, 106, 25, 7, 4, 'PRIORITY', 'MEDICAL', 2, '2026-11-16 06:34:00', '2026-11-16 06:38:00', 1, 5, 1, 'SCHEDULED', '2026-11-14 07:13:32');

-- --------------------------------------------------------

--
-- Table structure for table `scheduling_events`
--

CREATE TABLE `scheduling_events` (
  `event_id` int(11) NOT NULL,
  `flight_id` int(11) NOT NULL,
  `schedule_id` int(11) DEFAULT NULL,
  `event_type` enum('FLIGHT_ADDED','FLIGHT_QUEUED','SCHEDULE_STARTED','RUNWAY_ASSIGNED','ATC_ASSIGNED','EMERGENCY_TRIGGERED','RUNWAY_RELEASED','FLIGHT_COMPLETED','FLIGHT_DELAYED','SCHEDULE_CANCELLED') NOT NULL,
  `description` text DEFAULT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `terminals`
--

CREATE TABLE `terminals` (
  `terminal_id` int(11) NOT NULL,
  `airport_id` int(11) NOT NULL,
  `terminal_name` varchar(100) NOT NULL,
  `terminal_type` enum('DOMESTIC','INTERNATIONAL','MIXED') DEFAULT 'MIXED',
  `passenger_capacity` int(11) DEFAULT 0,
  `status` enum('OPERATIONAL','CLOSED','MAINTENANCE') DEFAULT 'OPERATIONAL',
  `created_at` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `terminals`
--

INSERT INTO `terminals` (`terminal_id`, `airport_id`, `terminal_name`, `terminal_type`, `passenger_capacity`, `status`, `created_at`) VALUES
(3, 25, 'Terminal 1', 'MIXED', 120, '', '2026-10-15 15:04:04'),
(4, 25, 'Terminal 2', 'INTERNATIONAL', 120, '', '2026-10-15 15:04:15');

-- --------------------------------------------------------

--
-- Table structure for table `weather_logs`
--

CREATE TABLE `weather_logs` (
  `weather_id` int(11) NOT NULL,
  `airport_id` int(11) NOT NULL,
  `weather_condition` varchar(100) NOT NULL,
  `visibility_km` decimal(6,2) DEFAULT NULL,
  `wind_speed_kmh` decimal(6,2) DEFAULT NULL,
  `wind_direction` int(11) DEFAULT NULL,
  `temperature_c` decimal(5,2) DEFAULT NULL,
  `severity` enum('LOW','MODERATE','HIGH','SEVERE') DEFAULT 'LOW',
  `recorded_at` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Indexes for dumped tables
--

--
-- Indexes for table `aircraft`
--
ALTER TABLE `aircraft`
  ADD PRIMARY KEY (`aircraft_id`),
  ADD UNIQUE KEY `registration_number` (`registration_number`),
  ADD KEY `fk_aircraft_airline` (`airline_id`);

--
-- Indexes for table `airlines`
--
ALTER TABLE `airlines`
  ADD PRIMARY KEY (`airline_id`),
  ADD UNIQUE KEY `airline_code` (`airline_code`);

--
-- Indexes for table `airports`
--
ALTER TABLE `airports`
  ADD PRIMARY KEY (`airport_id`),
  ADD UNIQUE KEY `airport_code` (`airport_code`);

--
-- Indexes for table `atc_controllers`
--
ALTER TABLE `atc_controllers`
  ADD PRIMARY KEY (`atc_id`),
  ADD UNIQUE KEY `employee_code` (`employee_code`),
  ADD KEY `fk_atc_airport` (`airport_id`);

--
-- Indexes for table `flights`
--
ALTER TABLE `flights`
  ADD PRIMARY KEY (`flight_id`),
  ADD KEY `fk_flight_airline` (`airline_id`),
  ADD KEY `fk_flight_aircraft` (`aircraft_id`),
  ADD KEY `fk_flight_terminal` (`terminal_id`),
  ADD KEY `fk_flight_gate` (`gate_id`),
  ADD KEY `idx_flights_status` (`status`),
  ADD KEY `idx_flights_priority` (`priority`),
  ADD KEY `idx_flights_arrival_time` (`arrival_time`),
  ADD KEY `idx_flights_departure_time` (`departure_time`),
  ADD KEY `idx_flights_airport` (`airport_id`);

--
-- Indexes for table `gates`
--
ALTER TABLE `gates`
  ADD PRIMARY KEY (`gate_id`),
  ADD KEY `fk_gate_terminal` (`terminal_id`);

--
-- Indexes for table `runways`
--
ALTER TABLE `runways`
  ADD PRIMARY KEY (`runway_id`),
  ADD UNIQUE KEY `uq_runway_code` (`airport_id`,`runway_code`),
  ADD KEY `idx_runways_status` (`status`);

--
-- Indexes for table `scheduler_runs`
--
ALTER TABLE `scheduler_runs`
  ADD PRIMARY KEY (`run_id`);

--
-- Indexes for table `schedules`
--
ALTER TABLE `schedules`
  ADD PRIMARY KEY (`schedule_id`),
  ADD KEY `fk_schedule_atc` (`atc_id`),
  ADD KEY `idx_schedules_algorithm` (`algorithm`),
  ADD KEY `idx_schedules_flight` (`flight_id`),
  ADD KEY `idx_schedules_runway` (`runway_id`),
  ADD KEY `fk_schedules_run` (`run_id`);

--
-- Indexes for table `scheduling_events`
--
ALTER TABLE `scheduling_events`
  ADD PRIMARY KEY (`event_id`),
  ADD KEY `fk_event_schedule` (`schedule_id`),
  ADD KEY `idx_events_flight` (`flight_id`);

--
-- Indexes for table `terminals`
--
ALTER TABLE `terminals`
  ADD PRIMARY KEY (`terminal_id`),
  ADD KEY `fk_terminal_airport` (`airport_id`);

--
-- Indexes for table `weather_logs`
--
ALTER TABLE `weather_logs`
  ADD PRIMARY KEY (`weather_id`),
  ADD KEY `idx_weather_airport` (`airport_id`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `aircraft`
--
ALTER TABLE `aircraft`
  MODIFY `aircraft_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=3;

--
-- AUTO_INCREMENT for table `airlines`
--
ALTER TABLE `airlines`
  MODIFY `airline_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=4;

--
-- AUTO_INCREMENT for table `airports`
--
ALTER TABLE `airports`
  MODIFY `airport_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=29;

--
-- AUTO_INCREMENT for table `atc_controllers`
--
ALTER TABLE `atc_controllers`
  MODIFY `atc_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=7;

--
-- AUTO_INCREMENT for table `flights`
--
ALTER TABLE `flights`
  MODIFY `flight_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=27;

--
-- AUTO_INCREMENT for table `gates`
--
ALTER TABLE `gates`
  MODIFY `gate_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=6;

--
-- AUTO_INCREMENT for table `runways`
--
ALTER TABLE `runways`
  MODIFY `runway_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=10;

--
-- AUTO_INCREMENT for table `scheduler_runs`
--
ALTER TABLE `scheduler_runs`
  MODIFY `run_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=108;

--
-- AUTO_INCREMENT for table `schedules`
--
ALTER TABLE `schedules`
  MODIFY `schedule_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=53;

--
-- AUTO_INCREMENT for table `scheduling_events`
--
ALTER TABLE `scheduling_events`
  MODIFY `event_id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `terminals`
--
ALTER TABLE `terminals`
  MODIFY `terminal_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=5;

--
-- AUTO_INCREMENT for table `weather_logs`
--
ALTER TABLE `weather_logs`
  MODIFY `weather_id` int(11) NOT NULL AUTO_INCREMENT;

--
-- Constraints for dumped tables
--

--
-- Constraints for table `aircraft`
--
ALTER TABLE `aircraft`
  ADD CONSTRAINT `fk_aircraft_airline` FOREIGN KEY (`airline_id`) REFERENCES `airlines` (`airline_id`) ON UPDATE CASCADE;

--
-- Constraints for table `atc_controllers`
--
ALTER TABLE `atc_controllers`
  ADD CONSTRAINT `fk_atc_airport` FOREIGN KEY (`airport_id`) REFERENCES `airports` (`airport_id`) ON DELETE CASCADE ON UPDATE CASCADE;

--
-- Constraints for table `flights`
--
ALTER TABLE `flights`
  ADD CONSTRAINT `fk_flight_aircraft` FOREIGN KEY (`aircraft_id`) REFERENCES `aircraft` (`aircraft_id`) ON UPDATE CASCADE,
  ADD CONSTRAINT `fk_flight_airline` FOREIGN KEY (`airline_id`) REFERENCES `airlines` (`airline_id`) ON UPDATE CASCADE,
  ADD CONSTRAINT `fk_flight_airport` FOREIGN KEY (`airport_id`) REFERENCES `airports` (`airport_id`) ON DELETE CASCADE ON UPDATE CASCADE,
  ADD CONSTRAINT `fk_flight_gate` FOREIGN KEY (`gate_id`) REFERENCES `gates` (`gate_id`) ON DELETE SET NULL ON UPDATE CASCADE,
  ADD CONSTRAINT `fk_flight_terminal` FOREIGN KEY (`terminal_id`) REFERENCES `terminals` (`terminal_id`) ON DELETE SET NULL ON UPDATE CASCADE;

--
-- Constraints for table `gates`
--
ALTER TABLE `gates`
  ADD CONSTRAINT `fk_gate_terminal` FOREIGN KEY (`terminal_id`) REFERENCES `terminals` (`terminal_id`) ON DELETE CASCADE ON UPDATE CASCADE;

--
-- Constraints for table `runways`
--
ALTER TABLE `runways`
  ADD CONSTRAINT `fk_runway_airport` FOREIGN KEY (`airport_id`) REFERENCES `airports` (`airport_id`) ON DELETE CASCADE ON UPDATE CASCADE;

--
-- Constraints for table `schedules`
--
ALTER TABLE `schedules`
  ADD CONSTRAINT `fk_schedule_atc` FOREIGN KEY (`atc_id`) REFERENCES `atc_controllers` (`atc_id`) ON DELETE SET NULL ON UPDATE CASCADE,
  ADD CONSTRAINT `fk_schedule_flight` FOREIGN KEY (`flight_id`) REFERENCES `flights` (`flight_id`) ON DELETE CASCADE ON UPDATE CASCADE,
  ADD CONSTRAINT `fk_schedule_runway` FOREIGN KEY (`runway_id`) REFERENCES `runways` (`runway_id`) ON UPDATE CASCADE,
  ADD CONSTRAINT `fk_schedules_run` FOREIGN KEY (`run_id`) REFERENCES `scheduler_runs` (`run_id`) ON DELETE CASCADE ON UPDATE CASCADE;

--
-- Constraints for table `scheduling_events`
--
ALTER TABLE `scheduling_events`
  ADD CONSTRAINT `fk_event_flight` FOREIGN KEY (`flight_id`) REFERENCES `flights` (`flight_id`) ON DELETE CASCADE ON UPDATE CASCADE,
  ADD CONSTRAINT `fk_event_schedule` FOREIGN KEY (`schedule_id`) REFERENCES `schedules` (`schedule_id`) ON DELETE SET NULL ON UPDATE CASCADE;

--
-- Constraints for table `terminals`
--
ALTER TABLE `terminals`
  ADD CONSTRAINT `fk_terminal_airport` FOREIGN KEY (`airport_id`) REFERENCES `airports` (`airport_id`) ON DELETE CASCADE ON UPDATE CASCADE;

--
-- Constraints for table `weather_logs`
--
ALTER TABLE `weather_logs`
  ADD CONSTRAINT `fk_weather_airport` FOREIGN KEY (`airport_id`) REFERENCES `airports` (`airport_id`) ON DELETE CASCADE ON UPDATE CASCADE;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
