from typing import Dict, List, Optional, Any
from datetime import datetime

from AutomationBuilder import AutomationBuilder

class WorkflowTemplates:
    """Pre-built workflow templates for common automation tasks."""
    
    def __init__(self):
        self.reference_time = datetime.fromisoformat("2024-12-23T03:51:25-06:00")
        self.builder = AutomationBuilder()

    def web_login(self, url: str, username: str, password: str) -> Dict[str, Any]:
        """Template for web login workflow."""
        return (self.builder.workflow()
            .add_step(self.builder.ui().type_text(username).build())
            .add_step(self.builder.ui().press_keys('Tab').build())
            .add_step(self.builder.ui().type_text(password).build())
            .add_step(self.builder.ui().click_text('Login').build())
            .run_sequential()
            .with_timeout(30)
            .with_retries(3)
            .build())

    def file_backup(self, source_dir: str, backup_dir: str) -> Dict[str, Any]:
        """Template for file backup workflow."""
        return (self.builder.workflow()
            .add_step(self.builder.data().sync_folders(source_dir, backup_dir).build())
            .add_step(self.builder.process().run_command('zip', ['-r', f'{backup_dir}.zip', backup_dir]).build())
            .run_sequential()
            .with_timeout(300)
            .build())

    def web_scrape_table(self, url: str, table_selector: str, 
                        output_file: str) -> Dict[str, Any]:
        """Template for web table scraping workflow."""
        return (self.builder.workflow()
            .add_step(self.builder.data().extract_table(url, table_selector).build())
            .add_step(self.builder.data()
                .transform_json('temp.json', output_file, [
                    {'type': 'filter_empty'},
                    {'type': 'format_dates'},
                    {'type': 'sort', 'key': 'date'}
                ]).build())
            .run_sequential()
            .with_timeout(60)
            .build())

    def system_monitor(self, process_name: str, 
                      alert_threshold: Dict[str, Any]) -> Dict[str, Any]:
        """Template for system monitoring workflow."""
        return (self.builder.workflow()
            .add_step(self.builder.process()
                .monitor_process(process_name, alert_threshold).build())
            .run_conditional(lambda x: x['cpu_usage'] > alert_threshold['cpu'])
            .with_timeout(3600)
            .build())

    def git_workflow(self, repo_path: str, branch: str, 
                    commit_msg: str) -> Dict[str, Any]:
        """Template for git operations workflow."""
        return (self.builder.workflow()
            .add_step(self.builder.process()
                .run_command('git', ['checkout', branch]).build())
            .add_step(self.builder.process()
                .run_command('git', ['pull', 'origin', branch]).build())
            .add_step(self.builder.process()
                .run_command('git', ['add', '.']).build())
            .add_step(self.builder.process()
                .run_command('git', ['commit', '-m', commit_msg]).build())
            .add_step(self.builder.process()
                .run_command('git', ['push', 'origin', branch]).build())
            .run_sequential()
            .with_timeout(120)
            .with_retries(3)
            .build())

    def data_validation(self, input_file: str, schema_file: str, 
                       output_file: str) -> Dict[str, Any]:
        """Template for data validation workflow."""
        return (self.builder.workflow()
            .add_step(self.builder.data()
                .validate_data(input_file, {'schema_file': schema_file}).build())
            .add_step(self.builder.data()
                .transform_json(input_file, output_file, [
                    {'type': 'remove_invalid'},
                    {'type': 'format_output'}
                ]).build())
            .run_sequential()
            .with_timeout(60)
            .build())

    def web_form_fill(self, form_data: Dict[str, str]) -> Dict[str, Any]:
        """Template for filling web forms."""
        workflow = self.builder.workflow()
        
        for field, value in form_data.items():
            workflow.add_step(self.builder.ui()
                .click_text(field, partial_match=True).build())
            workflow.add_step(self.builder.ui()
                .type_text(value).build())
            workflow.add_step(self.builder.ui()
                .press_keys('Tab').build())
        
        return (workflow
            .run_sequential()
            .with_timeout(120)
            .build())

    def file_monitor(self, directory: str, patterns: List[str], 
                    handler: Dict[str, Any]) -> Dict[str, Any]:
        """Template for file monitoring workflow."""
        return (self.builder.workflow()
            .add_step(self.builder.data()
                .monitor_file(directory, patterns).build())
            .add_step(handler)
            .run_conditional(lambda x: x['pattern_matched'])
            .with_timeout(3600)
            .build())

    def system_maintenance(self) -> Dict[str, Any]:
        """Template for system maintenance workflow."""
        return (self.builder.workflow()
            .add_step(self.builder.process()
                .run_command('cleanmgr', ['/sagerun:1']).build())
            .add_step(self.builder.process()
                .run_command('defrag', ['C:', '/U', '/V']).build())
            .add_step(self.builder.process()
                .run_command('chkdsk', ['C:', '/F']).build())
            .run_sequential()
            .with_timeout(7200)
            .build())

    def app_update(self, app_name: str, version: str) -> Dict[str, Any]:
        """Template for application update workflow."""
        return (self.builder.workflow()
            .add_step(self.builder.process()
                .run_command('taskkill', ['/IM', f'{app_name}.exe', '/F']).build())
            .add_step(self.builder.process()
                .run_command('msiexec', ['/i', f'{app_name}-{version}.msi', '/quiet']).build())
            .add_step(self.builder.process()
                .run_command(f'{app_name}.exe').build())
            .run_sequential()
            .with_timeout(300)
            .with_retries(2)
            .build())

# Example usage:
"""
templates = WorkflowTemplates()

# Web login workflow
login_task = templates.web_login(
    'https://example.com/login',
    'username',
    'password'
)

# Git workflow
git_task = templates.git_workflow(
    '/path/to/repo',
    'main',
    'Update documentation'
)

# System monitoring
monitor_task = templates.system_monitor(
    'important_service.exe',
    {'cpu': 80, 'memory': 90}
)

# Execute tasks
await computer_system.execute_action(login_task)
await computer_system.execute_action(git_task)
await computer_system.execute_action(monitor_task)
"""
