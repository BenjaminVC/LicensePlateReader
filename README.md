# Traffic Violation Detection System Simulation on AWS
## Overview
This project simulates a system that allows cities to use cameras at road intersections to identify and bill drivers who commit traffic violations at traffic lights. 
The simulation uses a hybrid cloud architecture to demonstrate the integration of various technologies and services.
## Features
- **License Plate Recognition**:Designed for traffic lights in California, recognizing plates with 7 characters (A-Z, 0-9) using **AWS Rekognition**.
- **Email Notifications**: Simulated violation notices sent via email.
- **Local DMV Database Integration**: Fetches driver email accounts from a mock DMV database.
- **AWS EventBridge Integration**: Non-California vehicle violations are sent to an AWS EventBridge bus.
- **Clean Image Processing**: Simulated cameras send "clean" license plate images to the system.
- **Metadata Tags**: Simulated cameras add 3 metadata tags to S3 bucket uploads: Location, DateTime, and Type of violation.
- **Violation Types & Fines**:
  - no_stop: $300.00
  - no_full_stop_on_right: $75.00
  - no_right_on_red: $125.00
## Email Format
```
Your vehicle was involved in a traffic violation. Please pay the specified ticket amount by 30 days:
Vehicle: [Color] [Make] [Model]
License plate: [PlateNumber]
Date: [DateTime]
Violation address: [Location]
Violation type: [Type]
Ticket amount: [Fine based on Type]
```

## Implementation Notes
- Use upload_data.py to simulate camera uploads, modified to include the 3 tags with each upload.
- Test with the provided 8 license plates (5 California, 3 non-California).
