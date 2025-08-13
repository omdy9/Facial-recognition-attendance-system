import geocoder

def get_current_location():
    g = geocoder.ip('me')  # Get current location based on IP
    return (g.latlng[0], g.latlng[1]) if g.latlng else None
