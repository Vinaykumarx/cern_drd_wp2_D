#!/usr/bin/env python3
from core.bootstrap import require_bootstrap; require_bootstrap()
"""
🎯 PROJECT STATUS DASHBOARD
FastAPI-based web dashboard for real-time project status monitoring

Run: uvicorn project_dashboard:app --reload --port 8888
Visit: http://localhost:8888
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import json
from pathlib import Path
from datetime import datetime
from project_agent import (
    ProjectStatusAgent, TaskStatus, Priority, TaskCategory,
    Task, KanbanBoard
)

# Initialize
app = FastAPI(title="Project Status Dashboard", version="1.0.0")
agent = ProjectStatusAgent()

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Pydantic Models
class TaskRequest(BaseModel):
    title: str
    description: str
    category: str
    priority: str
    estimated_hours: float = 0


class TaskUpdate(BaseModel):
    status: str
    assigned_to: Optional[str] = None


class TaskResponse(BaseModel):
    id: str
    title: str
    description: str
    status: str
    priority: str
    category: str
    assigned_to: Optional[str]
    estimated_hours: float
    created_date: str


# API Endpoints
@app.get("/api/health")
async def get_health():
    """Get project health status"""
    report = agent.run_full_assessment()
    health = report['project_health']
    return {
        'status': health['status'],
        'health_score': health['health_score'],
        'critical_issues': health['critical_issues'],
        'warnings': health['warnings'],
        'verified_components': health['verified_components'],
        'timestamp': datetime.now().isoformat(),
    }


@app.get("/api/stats")
async def get_stats():
    """Get task statistics"""
    report = agent.run_full_assessment()
    return {
        'stats': report['kanban_stats'],
        'total_estimated_hours': report['kanban_stats']['total_estimated_hours'],
        'timestamp': datetime.now().isoformat(),
    }


@app.get("/api/tasks")
async def get_tasks(status: Optional[str] = None):
    """Get all tasks or filter by status"""
    tasks = agent.kanban.tasks

    if status:
        try:
            status_enum = TaskStatus[status.upper()]
            tasks = {tid: t for tid, t in tasks.items() if t.status == status_enum}
        except KeyError:
            raise HTTPException(status_code=400, detail="Invalid status")

    return {
        'tasks': [
            {
                'id': task.id,
                'title': task.title,
                'description': task.description,
                'status': task.status.value,
                'priority': task.priority.value,
                'category': task.category.value,
                'assigned_to': task.assigned_to,
                'estimated_hours': task.estimated_hours,
                'created_date': task.created_date,
            }
            for task in tasks.values()
        ],
        'count': len(tasks),
    }


@app.get("/api/tasks/{task_id}")
async def get_task(task_id: str):
    """Get specific task"""
    if task_id not in agent.kanban.tasks:
        raise HTTPException(status_code=404, detail="Task not found")

    task = agent.kanban.tasks[task_id]
    return {
        'id': task.id,
        'title': task.title,
        'description': task.description,
        'status': task.status.value,
        'priority': task.priority.value,
        'category': task.category.value,
        'assigned_to': task.assigned_to,
        'estimated_hours': task.estimated_hours,
        'created_date': task.created_date,
    }


@app.post("/api/tasks")
async def create_task(task_req: TaskRequest):
    """Create new task"""
    try:
        category = TaskCategory[task_req.category.upper().replace(' ', '_')]
        priority = Priority[task_req.priority.upper()]
    except KeyError:
        raise HTTPException(status_code=400, detail="Invalid category or priority")

    task = agent.kanban.add_task(
        title=task_req.title,
        description=task_req.description,
        category=category,
        priority=priority,
        estimated_hours=task_req.estimated_hours,
    )

    return {
        'id': task.id,
        'status': 'created',
        'message': f'Task {task.id} created successfully',
    }


@app.put("/api/tasks/{task_id}")
async def update_task(task_id: str, task_update: TaskUpdate):
    """Update task"""
    if task_id not in agent.kanban.tasks:
        raise HTTPException(status_code=404, detail="Task not found")

    task = agent.kanban.tasks[task_id]

    if task_update.status:
        try:
            status_map = {s.value: s for s in TaskStatus}
            if task_update.status not in status_map:
                raise ValueError
            new_status = status_map[task_update.status]
            agent.kanban.update_task_status(task_id, new_status)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid status")

    if task_update.assigned_to:
        task.assigned_to = task_update.assigned_to
        agent.kanban.save_tasks()

    return {
        'id': task_id,
        'status': 'updated',
        'message': 'Task updated successfully',
    }


@app.get("/api/allocations")
async def get_allocations():
    """Get resource allocation recommendations"""
    report = agent.run_full_assessment()
    recs = report['resource_recommendations']

    return {
        'team': recs['team'],
        'recommendations': recs['recommendations'][:15],
        'total_recommendations': len(recs['recommendations']),
    }


@app.get("/api/report")
async def get_report():
    """Get full project report"""
    report = agent.run_full_assessment()
    return {
        'health': report['project_health'],
        'stats': report['kanban_stats'],
        'recommendations': report['resource_recommendations'],
        'timestamp': datetime.now().isoformat(),
    }


@app.get("/api/kanban")
async def get_kanban_view():
    """Get kanban board view"""
    tasks_by_status = {}
    for status in TaskStatus:
        tasks_by_status[status.value] = [
            {
                'id': t.id,
                'title': t.title,
                'description': t.description[:50] + '...' if len(t.description) > 50 else t.description,
                'priority': t.priority.value,
                'assigned_to': t.assigned_to,
                'estimated_hours': t.estimated_hours,
            }
            for t in agent.kanban.tasks.values() if t.status == status
        ]

    return tasks_by_status


# HTML Dashboard
@app.get("/")
async def dashboard():
    """Dashboard HTML"""
    return HTMLResponse("""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Project Status Dashboard</title>
        <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
        <style>
            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }
            
            body {
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
                background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
                color: #e2e8f0;
                min-height: 100vh;
                padding: 20px;
            }
            
            .container {
                max-width: 1400px;
                margin: 0 auto;
            }
            
            header {
                text-align: center;
                margin-bottom: 40px;
            }
            
            h1 {
                font-size: 2.5em;
                margin-bottom: 10px;
                background: linear-gradient(135deg, #60a5fa, #a78bfa);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                background-clip: text;
            }
            
            .subtitle {
                color: #94a3b8;
                font-size: 1em;
            }
            
            .status-section {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
                gap: 20px;
                margin-bottom: 40px;
            }
            
            .card {
                background: rgba(30, 41, 59, 0.8);
                border: 1px solid rgba(148, 163, 184, 0.2);
                border-radius: 12px;
                padding: 25px;
                backdrop-filter: blur(10px);
                transition: all 0.3s ease;
            }
            
            .card:hover {
                border-color: rgba(148, 163, 184, 0.5);
                transform: translateY(-2px);
            }
            
            .card-title {
                font-size: 1.2em;
                font-weight: 600;
                margin-bottom: 15px;
                color: #60a5fa;
            }
            
            .health-score {
                font-size: 3em;
                font-weight: bold;
                margin: 20px 0;
                color: #10b981;
            }
            
            .health-score.warning {
                color: #f59e0b;
            }
            
            .health-score.critical {
                color: #ef4444;
            }
            
            .task-list {
                list-style: none;
                margin-top: 15px;
            }
            
            .task-list li {
                padding: 10px;
                margin: 5px 0;
                background: rgba(51, 65, 85, 0.5);
                border-radius: 8px;
                font-size: 0.9em;
                border-left: 3px solid #60a5fa;
            }
            
            .stats-grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
                gap: 15px;
                margin-top: 15px;
            }
            
            .stat-box {
                background: rgba(51, 65, 85, 0.5);
                padding: 15px;
                border-radius: 8px;
                text-align: center;
            }
            
            .stat-number {
                font-size: 2em;
                font-weight: bold;
                color: #60a5fa;
                margin-bottom: 5px;
            }
            
            .stat-label {
                font-size: 0.85em;
                color: #94a3b8;
            }
            
            .kanban-container {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
                gap: 20px;
                margin-top: 30px;
            }
            
            .kanban-column {
                background: rgba(30, 41, 59, 0.5);
                border: 1px solid rgba(148, 163, 184, 0.2);
                border-radius: 8px;
                padding: 15px;
                min-height: 500px;
            }
            
            .kanban-header {
                font-weight: 600;
                color: #60a5fa;
                margin-bottom: 15px;
                padding-bottom: 10px;
                border-bottom: 1px solid rgba(148, 163, 184, 0.2);
            }
            
            .kanban-card {
                background: rgba(51, 65, 85, 0.7);
                border-left: 3px solid #60a5fa;
                padding: 12px;
                margin-bottom: 10px;
                border-radius: 6px;
                font-size: 0.85em;
                cursor: pointer;
                transition: all 0.2s ease;
            }
            
            .kanban-card:hover {
                background: rgba(51, 65, 85, 0.9);
                transform: translateX(4px);
            }
            
            .priority-critical {
                border-left-color: #ef4444;
            }
            
            .priority-high {
                border-left-color: #f59e0b;
            }
            
            .priority-medium {
                border-left-color: #eab308;
            }
            
            .priority-low {
                border-left-color: #10b981;
            }
            
            .chart-container {
                position: relative;
                height: 300px;
                margin-top: 20px;
            }
            
            .loading {
                text-align: center;
                color: #94a3b8;
                padding: 40px;
            }
            
            .error {
                background: rgba(239, 68, 68, 0.1);
                border: 1px solid rgba(239, 68, 68, 0.5);
                color: #fca5a5;
                padding: 15px;
                border-radius: 8px;
                margin-bottom: 20px;
            }
            
            .footer {
                text-align: center;
                margin-top: 40px;
                padding: 20px;
                color: #64748b;
                font-size: 0.9em;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <header>
                <h1>🤖 Project Status Agent</h1>
                <p class="subtitle">CERN Multimodal RAG - Production Readiness Dashboard</p>
            </header>
            
            <div id="error-container"></div>
            
            <div id="health-section" class="status-section">
                <div class="card loading">Loading health status...</div>
            </div>
            
            <div id="stats-section" class="status-section">
                <div class="card loading">Loading statistics...</div>
            </div>
            
            <div class="card">
                <div class="card-title">📊 Task Distribution</div>
                <div class="chart-container">
                    <canvas id="taskChart"></canvas>
                </div>
            </div>
            
            <div class="card" style="margin-top: 20px;">
                <div class="card-title">🎯 Kanban Board Preview</div>
                <div id="kanban-preview" style="margin-top: 15px;">
                    <p class="loading">Loading kanban board...</p>
                </div>
            </div>
            
            <div class="footer">
                Last updated: <span id="timestamp"></span> | 
                <a href="/docs" style="color: #60a5fa; text-decoration: none;">API Docs</a>
            </div>
        </div>
        
        <script>
            let taskChart = null;
            
            async function loadHealth() {
                try {
                    const response = await fetch('/api/health');
                    const data = await response.json();
                    
                    const healthSection = document.getElementById('health-section');
                    let healthClass = '';
                    if (data.health_score >= 90) {
                        healthClass = '';
                    } else if (data.health_score >= 70) {
                        healthClass = 'warning';
                    } else {
                        healthClass = 'critical';
                    }
                    
                    let issuesHtml = '';
                    if (data.critical_issues.length > 0) {
                        issuesHtml = '<div class="card" style="margin-top: 20px;"><div class="card-title">🚨 Critical Issues</div><ul class="task-list">';
                        data.critical_issues.forEach(issue => {
                            issuesHtml += '<li>' + issue + '</li>';
                        });
                        issuesHtml += '</ul></div>';
                    }
                    
                    healthSection.innerHTML = `
                        <div class="card">
                            <div class="card-title">💚 Project Health</div>
                            <div class="health-score ${healthClass}">${data.health_score.toFixed(1)}/100</div>
                            <div style="color: #94a3b8; text-align: center;">${data.status}</div>
                        </div>
                    ` + issuesHtml;
                } catch (error) {
                    console.error('Failed to load health:', error);
                }
            }
            
            async function loadStats() {
                try {
                    const response = await fetch('/api/stats');
                    const data = await response.json();
                    
                    const statsSection = document.getElementById('stats-section');
                    let html = '';
                    
                    for (const [status, count] of Object.entries(data.stats.by_status)) {
                        html += `
                            <div class="card">
                                <div class="card-title">${status}</div>
                                <div class="stat-box">
                                    <div class="stat-number">${count}</div>
                                </div>
                            </div>
                        `;
                    }
                    
                    statsSection.innerHTML = html;
                } catch (error) {
                    console.error('Failed to load stats:', error);
                }
            }
            
            async function loadCharts() {
                try {
                    const response = await fetch('/api/kanban');
                    const data = await response.json();
                    
                    const labels = Object.keys(data);
                    const counts = Object.values(data).map(tasks => tasks.length);
                    
                    const ctx = document.getElementById('taskChart').getContext('2d');
                    if (taskChart) {
                        taskChart.destroy();
                    }
                    taskChart = new Chart(ctx, {
                        type: 'bar',
                        data: {
                            labels: labels,
                            datasets: [{
                                label: 'Task Count',
                                data: counts,
                                backgroundColor: [
                                    '#ef4444', '#f59e0b', '#eab308', 
                                    '#10b981', '#06b6d4', '#8b5cf6'
                                ],
                                borderRadius: 6,
                            }]
                        },
                        options: {
                            responsive: true,
                            maintainAspectRatio: false,
                            plugins: {
                                legend: {
                                    display: false
                                }
                            },
                            scales: {
                                y: {
                                    beginAtZero: true,
                                    ticks: {
                                        color: '#94a3b8'
                                    },
                                    grid: {
                                        color: 'rgba(148, 163, 184, 0.1)'
                                    }
                                },
                                x: {
                                    ticks: {
                                        color: '#94a3b8'
                                    },
                                    grid: {
                                        display: false
                                    }
                                }
                            }
                        }
                    });
                } catch (error) {
                    console.error('Failed to load charts:', error);
                }
            }
            
            async function loadKanban() {
                try {
                    const response = await fetch('/api/kanban');
                    const data = await response.json();
                    
                    let html = '<div class="kanban-container">';
                    
                    for (const [status, tasks] of Object.entries(data)) {
                        html += `<div class="kanban-column">
                            <div class="kanban-header">${status}</div>`;
                        
                        tasks.slice(0, 5).forEach(task => {
                            const priorityClass = 'priority-' + task.priority.split(' ')[1].toLowerCase();
                            html += `
                                <div class="kanban-card ${priorityClass}">
                                    <strong>${task.id}</strong><br>
                                    ${task.title}<br>
                                    <span style="color: #94a3b8; font-size: 0.8em;">${task.priority}</span>
                                </div>
                            `;
                        });
                        
                        if (tasks.length > 5) {
                            html += `<div style="color: #64748b; padding: 10px; font-size: 0.85em;">+${tasks.length - 5} more</div>`;
                        }
                        
                        html += '</div>';
                    }
                    
                    html += '</div>';
                    document.getElementById('kanban-preview').innerHTML = html;
                } catch (error) {
                    console.error('Failed to load kanban:', error);
                }
            }
            
            async function loadDashboard() {
                await Promise.all([
                    loadHealth(),
                    loadStats(),
                    loadCharts(),
                    loadKanban()
                ]);
                
                document.getElementById('timestamp').textContent = new Date().toLocaleString();
            }
            
            // Load on page load
            loadDashboard();
            
            // Refresh every 30 seconds
            setInterval(loadDashboard, 30000);
        </script>
    </body>
    </html>
    """)


if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host='0.0.0.0', port=8888)
