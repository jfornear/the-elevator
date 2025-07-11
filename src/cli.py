#!/usr/bin/env python3
import click
import requests
import json
from typing import Optional
from tabulate import tabulate
from time import sleep

# Default API endpoint
DEFAULT_API_URL = "http://localhost:8080"

def format_elevator_status(status):
    """Format elevator status into a readable string."""
    return [
        status["id"],
        status["current_floor"],
        status["direction"],
        status["state"],
        ",".join(map(str, status["target_floors"])),
        "Open" if status["door_open"] else "Closed",
        status["zone"] or "None",
        str(status["zone_range"] or "None")
    ]

def print_elevator_status(status, single=False):
    """Print elevator status in a table format."""
    headers = ["ID", "Floor", "Direction", "State", "Targets", "Door", "Zone", "Zone Range"]
    if single:
        data = [format_elevator_status(status)]
    else:
        data = [format_elevator_status(e) for e in status["elevators"]]
    print(tabulate(data, headers=headers, tablefmt="grid"))

@click.group()
@click.option('--api-url', default=DEFAULT_API_URL, help='Base URL of the elevator API')
@click.pass_context
def cli(ctx, api_url):
    """
    CLI tool for interacting with the Elevator System API.
    
    Example usage:
    
    # Get system status:
    ./cli.py status
    
    # Get specific elevator status:
    ./cli.py elevator-status 1
    
    # Request elevator from inside (internal request):
    ./cli.py request-elevator 1 5  # Request elevator 1 to go to floor 5
    
    # Request elevator from floor (external request):
    ./cli.py call-elevator 3 up  # Call elevator to floor 3, going up
    
    # Get system statistics:
    ./cli.py stats
    
    # Monitor system status (updates every second):
    ./cli.py monitor
    
    # Trigger emergency mode:
    ./cli.py emergency
    
    # Resume normal operation:
    ./cli.py resume
    """
    ctx.ensure_object(dict)
    ctx.obj['API_URL'] = api_url.rstrip('/')

@cli.command()
@click.pass_context
def status(ctx):
    """Get current status of all elevators."""
    try:
        response = requests.get(f"{ctx.obj['API_URL']}/system/status")
        response.raise_for_status()
        print_elevator_status(response.json())
    except requests.RequestException as e:
        click.echo(f"Error: {str(e)}", err=True)

@cli.command()
@click.argument('elevator_id', type=int)
@click.pass_context
def elevator_status(ctx, elevator_id):
    """Get status of a specific elevator."""
    try:
        response = requests.get(f"{ctx.obj['API_URL']}/elevator/{elevator_id}/status")
        response.raise_for_status()
        print_elevator_status(response.json(), single=True)
    except requests.RequestException as e:
        click.echo(f"Error: {str(e)}", err=True)

@cli.command()
@click.argument('elevator_id', type=int)
@click.argument('target_floor', type=int)
@click.pass_context
def request_elevator(ctx, elevator_id, target_floor):
    """Request an elevator to a specific floor (internal request)."""
    try:
        response = requests.post(
            f"{ctx.obj['API_URL']}/elevator/{elevator_id}/request",
            json={"target_floor": target_floor}
        )
        response.raise_for_status()
        click.echo(response.json()["message"])
    except requests.RequestException as e:
        click.echo(f"Error: {str(e)}", err=True)

@cli.command()
@click.argument('floor_number', type=int)
@click.argument('direction', type=click.Choice(['up', 'down']))
@click.pass_context
def call_elevator(ctx, floor_number, direction):
    """Call an elevator from a floor (external request)."""
    try:
        response = requests.post(
            f"{ctx.obj['API_URL']}/floor/{floor_number}/request",
            params={"direction": direction}
        )
        response.raise_for_status()
        click.echo(response.json()["message"])
    except requests.RequestException as e:
        click.echo(f"Error: {str(e)}", err=True)

@cli.command()
@click.pass_context
def stats(ctx):
    """Get system statistics."""
    try:
        response = requests.get(f"{ctx.obj['API_URL']}/system/statistics")
        response.raise_for_status()
        stats = response.json()
        print("\nSystem Statistics:")
        print("=================")
        for key, value in stats.items():
            print(f"{key.replace('_', ' ').title()}: {value}")
    except requests.RequestException as e:
        click.echo(f"Error: {str(e)}", err=True)

@cli.command()
@click.option('--interval', default=1.0, help='Update interval in seconds')
@click.pass_context
def monitor(ctx, interval):
    """Monitor system status in real-time."""
    click.echo("Monitoring elevator system (Ctrl+C to stop)...")
    try:
        while True:
            click.clear()
            try:
                response = requests.get(f"{ctx.obj['API_URL']}/system/status")
                response.raise_for_status()
                print_elevator_status(response.json())
            except requests.RequestException as e:
                click.echo(f"Error: {str(e)}", err=True)
            sleep(interval)
    except KeyboardInterrupt:
        click.echo("\nMonitoring stopped.")

@cli.command()
@click.pass_context
def emergency(ctx):
    """Trigger emergency mode."""
    try:
        response = requests.post(f"{ctx.obj['API_URL']}/system/emergency")
        response.raise_for_status()
        click.echo(response.json()["message"])
    except requests.RequestException as e:
        click.echo(f"Error: {str(e)}", err=True)

@cli.command()
@click.pass_context
def resume(ctx):
    """Resume normal operation after emergency."""
    try:
        response = requests.post(f"{ctx.obj['API_URL']}/system/resume")
        response.raise_for_status()
        click.echo(response.json()["message"])
    except requests.RequestException as e:
        click.echo(f"Error: {str(e)}", err=True)

if __name__ == '__main__':
    cli(obj={}) 