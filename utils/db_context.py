from datetime import datetime, timezone
from models import Event, Club, Faculty, Alumni, Bus, AcademicResource, CommunityPost
import json

def get_database_context(user_message: str, user):
    """
    Analyze user message and fetch relevant database context
    """
    message_lower = user_message.lower()
    context = {}
    
    # Check for events-related queries
    if any(word in message_lower for word in ['event', 'events', 'happening', 'festival', 'fest', 'workshop', 'seminar']):
        upcoming_events = Event.query.filter(
            Event.event_date >= datetime.now(timezone.utc)
        ).order_by(Event.event_date.asc()).limit(5).all()
        
        if upcoming_events:
            context['upcoming_events'] = [{
                'title': e.title,
                'description': e.description,
                'date': e.event_date.strftime('%B %d, %Y at %I:%M %p'),
                'venue': e.venue,
                'type': e.event_type
            } for e in upcoming_events]
    
    # Check for clubs-related queries
    if any(word in message_lower for word in ['club', 'clubs', 'join', 'society', 'organization']):
        clubs = Club.query.all()
        if clubs:
            context['clubs'] = [{
                'name': c.name,
                'description': c.description,
                'type': c.club_type,
                'secretary': c.secretary.name if c.secretary else 'N/A',
                'members': len(c.memberships)
            } for c in clubs]
    
    # Check for faculty-related queries
    if any(word in message_lower for word in ['faculty', 'professor', 'teacher', 'staff', 'instructor']):
        faculty_members = Faculty.query.all()
        if faculty_members:
            context['faculty'] = [{
                'name': f.name,
                'designation': f.designation,
                'department': f.department,
                'subjects': f.subjects,
                'email': f.email,
                'office': f.office
            } for f in faculty_members]
    
    # Check for alumni-related queries
    if any(word in message_lower for word in ['alumni', 'alumnus', 'graduate', 'passed out']):
        alumni = Alumni.query.all()
        if alumni:
            context['alumni'] = [{
                'name': a.name,
                'batch': a.batch,
                'designation': a.current_designation,
                'company': a.company
            } for a in alumni]
    
    # Check for bus/transport-related queries
    if any(word in message_lower for word in ['bus', 'transport', 'route', 'travel']):
        buses = Bus.query.filter_by(is_active=True).all()
        if buses:
            context['buses'] = [{
                'number': b.bus_number,
                'route': b.route_description,
                'stops': [s.stop_name for s in b.stops]
            } for b in buses]
        
        if user.selected_bus:
            context['my_bus'] = {
                'number': user.selected_bus.bus_number,
                'stop': user.selected_stop,
                'route': user.selected_bus.route_description
            }
    
    # Check for academic resources
    if any(word in message_lower for word in ['notes', 'resource', 'study', 'material', 'book', 'syllabus', 'pyq']):
        if user.course and user.branch and user.year:
            resources = AcademicResource.query.filter_by(
                course=user.course,
                branch=user.branch,
                year=user.year
            ).limit(10).all()
            
            if resources:
                context['academic_resources'] = [{
                    'title': r.title,
                    'subject': r.subject,
                    'type': r.resource_type,
                    'views': r.views
                } for r in resources]
    
    # Check for community/posts
    if any(word in message_lower for word in ['post', 'community', 'announcement', 'news']):
        posts = CommunityPost.query.order_by(CommunityPost.created_at.desc()).limit(5).all()
        if posts:
            context['recent_posts'] = [{
                'author': p.author.name,
                'content': p.content[:100] + '...' if len(p.content) > 100 else p.content,
                'type': p.post_type,
                'likes': p.likes
            } for p in posts]
    
    return context


def format_context_for_ai(context: dict) -> str:
    """
    Format database context into a readable string for the AI
    """
    if not context:
        return ""
    
    formatted = "\n\n[Database Information]:\n"
    
    if 'upcoming_events' in context:
        formatted += "\nUpcoming Events:\n"
        for event in context['upcoming_events']:
            formatted += f"- {event['title']}: {event['description']}\n"
            formatted += f"  Date: {event['date']}, Venue: {event['venue']}\n"
    
    if 'clubs' in context:
        formatted += "\nCampus Clubs:\n"
        for club in context['clubs']:
            formatted += f"- {club['name']}: {club['description']}\n"
            formatted += f"  Type: {club['type']}, Secretary: {club['secretary']}, Members: {club['members']}\n"
    
    if 'faculty' in context:
        formatted += "\nFaculty Members:\n"
        for f in context['faculty']:
            formatted += f"- {f['name']} ({f['designation']}, {f['department']})\n"
            formatted += f"  Subjects: {f['subjects']}, Office: {f['office']}\n"
    
    if 'alumni' in context:
        formatted += "\nNotable Alumni:\n"
        for a in context['alumni']:
            formatted += f"- {a['name']} (Batch {a['batch']}): {a['designation']} at {a['company']}\n"
    
    if 'buses' in context:
        formatted += "\nAvailable Buses:\n"
        for bus in context['buses']:
            formatted += f"- Bus {bus['number']}: {bus['route']}\n"
    
    if 'my_bus' in context:
        formatted += f"\nYour Selected Bus: {context['my_bus']['number']}\n"
        formatted += f"Your Stop: {context['my_bus']['stop']}\n"
    
    if 'academic_resources' in context:
        formatted += "\nAvailable Study Materials:\n"
        for r in context['academic_resources']:
            formatted += f"- {r['title']} ({r['subject']}) - {r['type']}\n"
    
    if 'recent_posts' in context:
        formatted += "\nRecent Community Posts:\n"
        for p in context['recent_posts']:
            formatted += f"- {p['author']}: {p['content']}\n"
    
    return formatted
