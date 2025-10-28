# Using the Dashboard

This guide walks you through using all the features of the Cloud Cleaner Dashboard effectively.

## Getting Started

### Accessing the Dashboard

1. **Open your browser** and navigate to [http://localhost:3000/dashboard](http://localhost:3000/dashboard)
2. **Wait for loading**: The dashboard will automatically scan your AWS resources
3. **View statistics**: You'll see summary cards showing resource counts

## Main Dashboard Overview

### Statistics Cards

The dashboard displays summary cards for each resource type:

- **🖥️ EC2 Instances**: Count of stopped instances across all regions
- **💾 EBS Volumes**: Count of unattached volumes across all regions  
- **🪣 S3 Buckets**: Count of unused buckets (global)
- **👥 IAM Users**: Count of inactive users (global)
- **🔑 Access Keys**: Count of unused keys with security risk indicators

### Resource Tabs

Click on any resource tab to view detailed information:

#### EC2 Instances Tab
- **Instance Details**: ID, Name, Type, Availability Zone
- **Creation Date**: When the instance was created
- **State Information**: Current state and transition reasons
- **Regional Filtering**: Filter by specific AWS regions

#### EBS Volumes Tab
- **Volume Details**: ID, Size, Type, Availability Zone
- **Encryption Status**: Whether the volume is encrypted
- **Attachment Status**: Current attachment state
- **Creation Date**: When the volume was created

#### S3 Buckets Tab
- **Bucket Details**: Name, Region, Creation Date
- **Usage Status**: Empty buckets or unused buckets
- **Last Access**: When the bucket was last accessed

#### IAM Users Tab
- **User Details**: Name, ARN, Creation Date
- **Access Status**: Console and programmatic access
- **Access Keys**: Count and status of access keys
- **Groups**: IAM groups the user belongs to

#### Access Keys Tab
- **Key Details**: Key ID, User Name, Status
- **Security Risk**: High/Low risk assessment
- **Last Used**: When the key was last used
- **Creation Date**: When the key was created

## Using Advanced Features

### Search and Filtering

#### Search Bar
- **Real-time Search**: Type in the search bar to filter resources
- **Search Fields**: Searches across names, IDs, ARNs, and metadata
- **Clear Search**: Click the X button to clear search

#### Filter System
- **Region Filter**: Select specific AWS regions
- **Status Filter**: Filter by resource status
- **Date Filters**: Filter by creation or last used dates
- **Security Filters**: Filter by security risk levels

#### Filter Management
- **Active Filter Indicators**: See which filters are currently applied
- **Result Counting**: View filtered vs. total resource counts
- **Clear All**: Reset all filters with one click

### Resource Details

#### Opening Resource Details
- **Click any resource** in the table to open a detailed modal
- **View comprehensive information** including metadata, policies, and tags

#### IAM Role Details
- **Basic Information**: Name, ARN, Description, Creation Date
- **Usage Statistics**: Last used date and region
- **Attached Policies**: Managed policies attached to the role
- **Inline Policies**: Custom policies defined on the role
- **Trust Relationships**: Assume role policy document
- **Tags**: All tags assigned to the role

#### IAM User Details
- **Basic Information**: Name, ARN, Creation Date
- **Access Information**: Console access status and last login
- **Access Keys**: List of access keys with status and dates
- **Groups**: IAM groups the user belongs to
- **Attached Policies**: Managed policies attached to the user
- **Tags**: All tags assigned to the user

### Resource Management

#### Safe Deletion
- **Delete Buttons**: Available for IAM roles and users
- **Force Cleanup**: Remove dependencies before deletion
- **Confirmation Required**: Double-check before deletion

#### Bulk Operations
- **Multi-Select**: Select multiple resources for bulk actions
- **Bulk Delete**: Remove multiple resources simultaneously
- **Export Data**: Export resource lists to CSV/JSON

## Alert Panel

### Sending Notifications

The Alert Panel allows you to send resource summaries to configured channels:

#### Using the Alert Panel
1. **Navigate to the Alert Panel** at the bottom of the dashboard
2. **Review Resource Summary**: Check counts and estimated savings
3. **Choose Notification Channel**:
   - **💬 Send to Slack**: Send to your Slack workspace
   - **📧 Send to Email**: Send to configured email recipients

#### Resource Summary Information
- **Total Resources**: Combined count of all unused resources
- **Regional Breakdown**: Resources by AWS region
- **Security Risks**: High-risk access keys highlighted
- **Estimated Savings**: Potential monthly cost savings

#### Setup Guide
- **Click "📖 Setup Guide"** for step-by-step configuration
- **Slack Setup**: Guided setup for Slack webhooks
- **Email Setup**: Instructions for various email providers

## Schedule Settings

### Configuring Automated Scanning

The Schedule Settings component allows you to automate resource monitoring:

#### Accessing Schedule Settings
- **Navigate to Schedule Settings** in the dashboard
- **View current configuration** and status

#### Configuration Options

**Enable/Disable Scanning**
- **Toggle Switch**: Turn automated scanning on/off
- **Status Display**: See current enabled/disabled state

**Frequency Settings**
- **Hourly**: Scan every hour
- **Daily**: Scan once per day
- **Weekly**: Scan once per week  
- **Custom**: Set custom interval in minutes

**Notification Channels**
- **Slack**: Send alerts to Slack workspace
- **Email**: Send detailed reports via email
- **Both**: Use both notification channels

**Status Monitoring**
- **Last Scan**: When the last scan was performed
- **Next Scan**: When the next scan is scheduled
- **Manual Trigger**: Run a scan immediately

#### Using Schedule Settings
1. **Enable the toggle** to turn on automated scanning
2. **Select frequency** from the dropdown
3. **Choose notification channels** with checkboxes
4. **Save settings** with the "Save Settings" button
5. **Monitor status** in the status cards
6. **Trigger manual scan** with the "Scan Now" button

## Navigation and UI

### Navigation Structure
- **Dashboard**: Main resource overview and monitoring
- **Settings**: Configuration and preferences

### Responsive Design
- **Desktop**: Full feature set with side-by-side layouts
- **Tablet**: Optimized for touch interaction
- **Mobile**: Simplified interface with essential features

### Loading States
- **Skeleton Loading**: Visual placeholders while loading
- **Progress Indicators**: Show scan progress
- **Error States**: Handle failed operations gracefully

### Notifications
- **Toast Notifications**: Success/error messages
- **Real-time Updates**: Automatic refresh when data changes
- **Status Messages**: Operation feedback and confirmations

## Best Practices

### Regular Monitoring
1. **Set up automated scanning** for continuous monitoring
2. **Review alerts promptly** to address security risks
3. **Schedule regular reviews** of unused resources
4. **Document cleanup procedures** for your team

### Security Considerations
1. **Focus on high-risk access keys** (active unused keys)
2. **Review IAM user access** regularly
3. **Monitor resource creation** and usage patterns
4. **Implement proper deletion procedures**

### Cost Optimization
1. **Identify long-running unused resources**
2. **Calculate potential savings** using the alert summaries
3. **Plan cleanup schedules** to minimize service disruption
4. **Track cost savings** over time

## Troubleshooting Common Issues

### Dashboard Not Loading
- **Check backend status**: Verify API is running
- **Check browser console** for JavaScript errors
- **Refresh the page** to reload data

### No Resources Showing
- **Verify AWS permissions** have required read access
- **Check AWS credentials** are valid and have permissions
- **Try different regions** if filtering by region

### Notification Issues
- **Verify webhook URLs** are correctly configured
- **Test email settings** using the setup guide
- **Check notification logs** in backend

### Slow Performance
- **Large AWS accounts** may take time to scan
- **Check network connectivity** to AWS APIs
- **Review browser performance** and clear cache

## Tips and Tricks

### Keyboard Shortcuts
- **Ctrl+F**: Focus search bar
- **Escape**: Clear current search/filters
- **Ctrl+R**: Refresh dashboard data

### Dashboard Customization
- **Bookmark filtered views** for frequent searches
- **Use browser bookmarks** for quick access
- **Pin dashboard** to browser favorites

### Efficient Workflows
1. **Start with global view** to get overview
2. **Use filters** to focus on specific concerns
3. **Review details** before taking action
4. **Set up automation** for ongoing monitoring
5. **Regular review** of scheduled scan results

## Integration Examples

### Slack Integration Tips
- **Create dedicated channel** for cloud cleaner alerts
- **Use channel notifications** for immediate awareness
- **Pin important alerts** for team reference

### Email Report Usage
- **Schedule regular reviews** of email reports
- **Forward reports** to relevant team members
- **Archive reports** for compliance and tracking

### Team Collaboration
- **Share dashboard access** with team members
- **Coordinate cleanup efforts** using scheduled alerts
- **Document procedures** for consistent approach