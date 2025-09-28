"use client"

import { useEffect, useState } from "react"
import { supabase } from "@/lib/supabaseClient"
import type { User } from "@supabase/supabase-js"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Slider } from "@/components/ui/slider"
import { Checkbox } from "@/components/ui/checkbox"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Badge } from "@/components/ui/badge"
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Sheet, SheetContent, SheetHeader, SheetTitle, SheetTrigger } from "@/components/ui/sheet"
import { Heart, X, MapPin, Star, Moon, Sun, Loader2, Phone, CheckCircle, XCircle, AlertCircle, Home, ExternalLink } from "lucide-react"
import { useApartments } from "@/lib/useApartments"
import { formatApartmentForDisplay } from "@/lib/apartmentService"

interface RoommateProfile {
  id: string
  name: string
  year: string
  major: string
  budget: number
  cleanliness: number
  noise_level: number
  study_time: number
  social_level: number
  sleep_schedule: number
  tags: string[]
}

interface RoommateMatch {
  id: string
  name: string
  year: string
  major: string
  budget: number
  compatibility_percentage: number
  preferences: {
    cleanliness: number
    noise_level: number
    study_time: number
    social_level: number
    sleep_schedule: number
  }
}

interface ApartmentMatch {
  apartment_name: string
  apartment_address: string
  bedroom_count: number
  price: string
  distance_to_vt: number
  amenities: string[]
  match_score: number
  match_percentage: number
  reasons: string[]
  roommate_compatibility: number
  apartment_features: any
}

const API_BASE_URL = process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000'

const preferenceOptions = [
  { value: 'VERY_LOW', label: 'Very Low' },
  { value: 'LOW', label: 'Low' },
  { value: 'MEDIUM', label: 'Medium' },
  { value: 'HIGH', label: 'High' },
  { value: 'VERY_HIGH', label: 'Very High' }
]

function RoommateMatchingInterface() {
  const [profile, setProfile] = useState({
    name: '',
    email: '',
    budget_min: 800,
    budget_max: 1200,
    preferred_bedrooms: 2,
    cleanliness: 'MEDIUM',
    noise_level: 'MEDIUM',
    study_time: 'MEDIUM',
    social_level: 'MEDIUM',
    sleep_schedule: 'MEDIUM',
    pet_friendly: false,
    smoking: false,
    year: 'Junior',
    major: 'Computer Science',
    max_distance_to_vt: 5.0,
    preferred_amenities: []
  })

  const [roommateMatches, setRoommateMatches] = useState<RoommateMatch[]>([])
  const [apartmentMatches, setApartmentMatches] = useState<ApartmentMatch[]>([])
  const [loading, setLoading] = useState(false)
  const [activeTab, setActiveTab] = useState('profile')
  const [currentProfileId, setCurrentProfileId] = useState<string>('')

  const handleCreateProfile = async () => {
    // Clear previous matches when creating a new profile
    setRoommateMatches([])
    setApartmentMatches([])
    setCurrentProfileId('')
    
    setLoading(true)
    try {
      // Ensure user is signed in to create a Supabase profile row
      const { data } = await supabase.auth.getSession()
      const token = data.session?.access_token
      if (!token) {
        alert('You need to sign in first')
        setLoading(false)
        return
      }

      // Helpers to map preference strings to integers for Supabase profiles table
      const convertPreferenceToInt = (value: string) => {
        const v = String(value).toUpperCase()
        if (v === 'VERY_LOW') return 1
        if (v === 'LOW') return 2
        if (v === 'MEDIUM') return 3
        if (v === 'HIGH') return 4
        return 5
      }

      // 1) Create/update profile row in Supabase via backend
      const profilesPayload = {
        name: profile.name,
        year: profile.year,
        major: profile.major,
        budget: profile.budget_min,
        move_in: null as any,
        tags: [] as string[],
        cleanliness: convertPreferenceToInt(profile.cleanliness as any),
        noise: convertPreferenceToInt(profile.noise_level as any),
        study_time: convertPreferenceToInt(profile.study_time as any),
        social: convertPreferenceToInt(profile.social_level as any),
        sleep: convertPreferenceToInt(profile.sleep_schedule as any),
      }

      const profilesResp = await fetch(`${API_BASE_URL}/profiles`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify(profilesPayload),
      })

      if (!profilesResp.ok) {
        const text = await profilesResp.text()
        console.error('Failed to create profile in Supabase profiles table:', text)
        alert(`Failed to create profile (profiles table): ${text}`)
        setLoading(false)
        return
      }

      const createdProfile = await profilesResp.json()
      setCurrentProfileId(createdProfile?.id || '')

      // 2) Store preferences for matching and fetch matches
      const roommateProfileData = {
        name: profile.name || 'User',
        email: data.session?.user?.email || '',
        budget_min: profile.budget_min,
        budget_max: profile.budget_max,
        preferred_bedrooms: profile.preferred_bedrooms,
        cleanliness: profile.cleanliness,
        noise_level: profile.noise_level,
        study_time: profile.study_time,
        social_level: profile.social_level,
        sleep_schedule: profile.sleep_schedule,
        pet_friendly: profile.pet_friendly,
        smoking: profile.smoking,
        year: profile.year,
        major: profile.major,
        max_distance_to_vt: profile.max_distance_to_vt,
        preferred_amenities: profile.preferred_amenities,
      }

      const response = await fetch(`${API_BASE_URL}/matching/roommate-preferences`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(roommateProfileData),
      })

      if (!response.ok) {
        const errorText = await response.text()
        alert(`Error: ${errorText || 'Failed to create profile'}`)
        setLoading(false)
        return
      }

      alert('Profile created successfully! Finding your perfect matches...')
      setActiveTab('roommates')
      await fetchRoommateMatches(roommateProfileData)
      await fetchApartmentMatches()
    } catch (error) {
      alert(`Error: ${error}`)
    } finally {
      setLoading(false)
    }
  }

  const fetchRoommateMatches = async (profileData?: any) => {
    try {
      // Clear previous matches first
      setRoommateMatches([])
      
      const dataToSend = profileData || profile
      
      console.log('🔍 Sending profile data:', dataToSend)
      
      const response = await fetch(`${API_BASE_URL}/matching/roommate-matches`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          ...dataToSend,
          min_compatibility: 0.5
        }),
      })

      if (response.ok) {
        const data = await response.json()
        setRoommateMatches(data.matches)
      }
    } catch (error) {
      console.error('Error fetching roommate matches:', error)
    }
  }

  const fetchApartmentMatches = async () => {
    try {
      // Create a complete profile object with all preferences for apartment matching
      const apartmentProfileData = {
        name: profile.name || 'User',
        email: profile.email || '',
        budget_min: profile.budget_min,
        budget_max: profile.budget_max,
        preferred_bedrooms: profile.preferred_bedrooms,
        cleanliness: profile.cleanliness,
        noise_level: profile.noise_level,
        study_time: profile.study_time,
        social_level: profile.social_level,
        sleep_schedule: profile.sleep_schedule,
        pet_friendly: profile.pet_friendly,
        smoking: profile.smoking,
        year: profile.year,
        major: profile.major,
        max_distance_to_vt: profile.max_distance_to_vt,
        preferred_amenities: profile.preferred_amenities
      }

      // Use the new apartment matching endpoint that works with user preferences
      const response = await fetch(`${API_BASE_URL}/matching/apartment-matches-for-preferences`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(apartmentProfileData),
      })

      if (response.ok) {
        const data = await response.json()
        setApartmentMatches(data.matches)
      }
    } catch (error) {
      console.error('Error fetching apartment matches:', error)
    }
  }

  const getCompatibilityColor = (percentage: number) => {
    if (percentage >= 80) return 'bg-green-500'
    if (percentage >= 60) return 'bg-yellow-500'
    return 'bg-red-500'
  }

  return (
    <div className="space-y-8">
      <div className="text-center mb-8">
        <h2 className="text-3xl font-bold mb-4">Smart Roommate Matching</h2>
        <p className="text-muted-foreground mb-6 max-w-2xl mx-auto">
          Create your profile and let our AI find your perfect roommate matches based on lifestyle, preferences, and compatibility.
        </p>
      </div>

      <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
        <TabsList className="grid w-full grid-cols-3 h-12 p-1 bg-muted/50">
          <TabsTrigger value="profile" className="font-medium">Create Profile</TabsTrigger>
          <TabsTrigger value="roommates" className="font-medium">Roommate Matches</TabsTrigger>
          <TabsTrigger value="apartments" className="font-medium">Apartment Matches</TabsTrigger>
        </TabsList>

        <TabsContent value="profile" className="mt-6">
          <Card>
            <CardHeader>
              <CardTitle>Create Your Roommate Profile</CardTitle>
            </CardHeader>
            <CardContent className="pt-0 space-y-6">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="space-y-2">
                  <Label htmlFor="name">Name</Label>
                  <Input
                    id="name"
                    placeholder="Your full name"
                    value={profile.name}
                    onChange={(e) => setProfile({ ...profile, name: e.target.value })}
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="email">Email</Label>
                  <Input
                    id="email"
                    type="email"
                    placeholder="your.email@vt.edu"
                    value={profile.email}
                    onChange={(e) => setProfile({ ...profile, email: e.target.value })}
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="budget_min">Minimum Budget ($/month)</Label>
                  <Input
                    id="budget_min"
                    type="number"
                    value={profile.budget_min}
                    onChange={(e) => setProfile({ ...profile, budget_min: parseInt(e.target.value) })}
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="budget_max">Maximum Budget ($/month)</Label>
                  <Input
                    id="budget_max"
                    type="number"
                    value={profile.budget_max}
                    onChange={(e) => setProfile({ ...profile, budget_max: parseInt(e.target.value) })}
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="bedrooms">Preferred Bedrooms</Label>
                  <Select
                    value={profile.preferred_bedrooms?.toString()}
                    onValueChange={(value) => setProfile({ ...profile, preferred_bedrooms: parseInt(value) })}
                  >
                    <SelectTrigger>
                      <SelectValue placeholder="Select bedroom count" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="1">1 Bedroom</SelectItem>
                      <SelectItem value="2">2 Bedrooms</SelectItem>
                      <SelectItem value="3">3 Bedrooms</SelectItem>
                      <SelectItem value="4">4 Bedrooms</SelectItem>
                      <SelectItem value="5">5 Bedrooms</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                <div className="space-y-2">
                  <Label htmlFor="year">Academic Year</Label>
                  <Select
                    value={profile.year}
                    onValueChange={(value) => setProfile({ ...profile, year: value })}
                  >
                    <SelectTrigger>
                      <SelectValue placeholder="Select academic year" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="Freshman">Freshman</SelectItem>
                      <SelectItem value="Sophomore">Sophomore</SelectItem>
                      <SelectItem value="Junior">Junior</SelectItem>
                      <SelectItem value="Senior">Senior</SelectItem>
                      <SelectItem value="Graduate">Graduate</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                <div className="space-y-2">
                  <Label htmlFor="major">Major</Label>
                  <Input
                    id="major"
                    placeholder="Your major"
                    value={profile.major}
                    onChange={(e) => setProfile({ ...profile, major: e.target.value })}
                  />
                </div>
                <div className="space-y-2">
                  <Label>Cleanliness Level</Label>
                  <Select
                    value={profile.cleanliness}
                    onValueChange={(value) => setProfile({ ...profile, cleanliness: value as any })}
                  >
                    <SelectTrigger>
                      <SelectValue placeholder="Select cleanliness level" />
                    </SelectTrigger>
                    <SelectContent>
                      {preferenceOptions.map(option => (
                        <SelectItem key={option.value} value={option.value}>{option.label}</SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
                <div className="space-y-2">
                  <Label>Noise Tolerance</Label>
                  <Select
                    value={profile.noise_level}
                    onValueChange={(value) => setProfile({ ...profile, noise_level: value as any })}
                  >
                    <SelectTrigger>
                      <SelectValue placeholder="Select noise tolerance" />
                    </SelectTrigger>
                    <SelectContent>
                      {preferenceOptions.map(option => (
                        <SelectItem key={option.value} value={option.value}>{option.label}</SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
                <div className="space-y-2">
                  <Label>Study Time</Label>
                  <Select
                    value={profile.study_time}
                    onValueChange={(value) => setProfile({ ...profile, study_time: value as any })}
                  >
                    <SelectTrigger>
                      <SelectValue placeholder="Select study time preference" />
                    </SelectTrigger>
                    <SelectContent>
                      {preferenceOptions.map(option => (
                        <SelectItem key={option.value} value={option.value}>{option.label}</SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
                <div className="space-y-2">
                  <Label>Social Level</Label>
                  <Select
                    value={profile.social_level}
                    onValueChange={(value) => setProfile({ ...profile, social_level: value as any })}
                  >
                    <SelectTrigger>
                      <SelectValue placeholder="Select social level" />
                    </SelectTrigger>
                    <SelectContent>
                      {preferenceOptions.map(option => (
                        <SelectItem key={option.value} value={option.value}>{option.label}</SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
                <div className="space-y-2">
                  <Label>Sleep Schedule</Label>
                  <Select
                    value={profile.sleep_schedule}
                    onValueChange={(value) => setProfile({ ...profile, sleep_schedule: value as any })}
                  >
                    <SelectTrigger>
                      <SelectValue placeholder="Select sleep schedule" />
                    </SelectTrigger>
                    <SelectContent>
                      {preferenceOptions.map(option => (
                        <SelectItem key={option.value} value={option.value}>{option.label}</SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
              </div>
              <div className="flex items-center space-x-6">
                <div className="flex items-center space-x-2">
                  <Checkbox
                    id="pet_friendly"
                    checked={profile.pet_friendly}
                    onCheckedChange={(checked) => setProfile({ ...profile, pet_friendly: checked as boolean })}
                  />
                  <Label htmlFor="pet_friendly">Pet Friendly</Label>
                </div>
                <div className="flex items-center space-x-2">
                  <Checkbox
                    id="smoking"
                    checked={profile.smoking}
                    onCheckedChange={(checked) => setProfile({ ...profile, smoking: checked as boolean })}
                  />
                  <Label htmlFor="smoking">Smoking</Label>
                </div>
              </div>
              <Button onClick={handleCreateProfile} className="w-full" disabled={loading}>
                {loading ? 'Creating Profile...' : 'Create Profile & Find Matches'}
              </Button>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="roommates" className="mt-6">
          <div className="flex justify-between items-center mb-4">
            <h2 className="text-2xl font-bold">Roommate Matches</h2>
            {roommateMatches.length > 0 && (
              <Button 
                variant="outline" 
                size="sm"
                onClick={() => {
                  setRoommateMatches([])
                  setApartmentMatches([])
                  setCurrentProfileId('')
                }}
              >
                Clear Results
              </Button>
            )}
          </div>
          {roommateMatches.length === 0 ? (
            <p className="text-gray-500">No roommate matches found yet. Create your profile to see matches!</p>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {roommateMatches.map((match) => (
                <Card key={match.id}>
                  <CardHeader>
                    <CardTitle className="flex items-center justify-between">
                      <span>{match.name}</span>
                      <Badge className={getCompatibilityColor(match.compatibility_percentage)}>
                        {match.compatibility_percentage}% Compatible
                      </Badge>
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-4">
                      <div className="space-y-1 text-sm">
                        <p><strong>Year:</strong> {match.year}</p>
                        <p><strong>Major:</strong> {match.major}</p>
                        <p><strong>Budget:</strong> ${match.budget}/month</p>
                        <p><strong>Cleanliness:</strong> {match.preferences.cleanliness}/5</p>
                        <p><strong>Noise Level:</strong> {match.preferences.noise_level}/5</p>
                        <p><strong>Study Time:</strong> {match.preferences.study_time}/5</p>
                        <p><strong>Social Level:</strong> {match.preferences.social_level}/5</p>
                        <p><strong>Sleep Schedule:</strong> {match.preferences.sleep_schedule}/5</p>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          )}
        </TabsContent>

        <TabsContent value="apartments" className="mt-6">
          <div className="flex justify-between items-center mb-4">
            <h2 className="text-2xl font-bold">Apartment Matches</h2>
            {apartmentMatches.length > 0 && (
              <Button 
                variant="outline" 
                size="sm"
                onClick={() => {
                  setApartmentMatches([])
                  setRoommateMatches([])
                  setCurrentProfileId('')
                }}
              >
                Clear Results
              </Button>
            )}
          </div>
          {apartmentMatches.length === 0 ? (
            <p className="text-gray-500">No apartment matches found yet. Create your profile to see recommendations!</p>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {apartmentMatches.map((apartment) => (
                <Card key={apartment.apartment_name}>
                  <CardHeader>
                    <CardTitle className="flex items-center justify-between">
                      <span>{apartment.apartment_name}</span>
                      <Badge className={getCompatibilityColor(apartment.match_percentage)}>
                        {apartment.match_percentage}% Match
                      </Badge>
                    </CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-2 text-sm">
                    <p><strong>Address:</strong> {apartment.apartment_address}</p>
                    <p><strong>Price:</strong> {apartment.price}</p>
                    <p><strong>Bedrooms:</strong> {apartment.bedroom_count}</p>
                    <p><strong>Distance to VT:</strong> {apartment.distance_to_vt} miles</p>
                    <p><strong>Amenities:</strong> {apartment.amenities.join(', ') || 'None'}</p>
                    <div className="mt-4">
                      <h5 className="font-medium mb-1">Reasons for Match:</h5>
                      <ul className="list-disc list-inside text-xs text-gray-600">
                        {apartment.reasons.map((reason, index) => (
                          <li key={index}>{reason}</li>
                        ))}
                      </ul>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          )}
        </TabsContent>
      </Tabs>
    </div>
  )
}

export default function HokieNest() {
  const [currentView, setCurrentView] = useState<"landing" | "onboarding" | "dashboard">("landing")
  const [user, setUser] = useState<User | null>(null)
  const [selectedProperty, setSelectedProperty] = useState<any>(null)
  const [darkMode, setDarkMode] = useState(false)
  const [authLoading, setAuthLoading] = useState(false)
  const [activeTab, setActiveTab] = useState("roommates")
  const [callingPropertyId, setCallingPropertyId] = useState<string | null>(null)
  const [housingMatches, setHousingMatches] = useState<Record<string, { match_percentage: number; reasons: string[] }>>({})
  
  // Fetch apartment data
  const { apartments, loading: apartmentsLoading, error: apartmentsError } = useApartments()
  const [preferences, setPreferences] = useState({
    cleanliness: [3],
    noiseLevel: [3],
    studyTime: [3],
    socialLevel: [3],
    sleepSchedule: [3],
  })
  const [selectedYear, setSelectedYear] = useState<string>("")
  const [maxDistanceToVt, setMaxDistanceToVt] = useState<number>(5.0)
  const [preferredAmenities, setPreferredAmenities] = useState<string[]>([])
  const [preferredBedrooms, setPreferredBedrooms] = useState<number>(2)
  const [roommateMatches, setRoommateMatches] = useState<RoommateMatch[]>([])
  const [apartmentMatches, setApartmentMatches] = useState<any[]>([])

  const checkUserProfile = async (sessionUser: User | null) => {
    if (!sessionUser) return null

    try {
      const { data } = await supabase.auth.getSession()
      const token = data.session?.access_token
      if (!token) return null

      const resp = await fetch(`${process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000'}/profiles/me`, {
        headers: {
          Authorization: `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      })

      if (!resp.ok) return null

      const profile = await resp.json()
      return profile?.id ? profile : null
    } catch (e) {
      console.error('checkUserProfile failed', e)
      return null
    }
  }

  useEffect(() => {
    let isMounted = true

    const handleAuthCallback = async () => {
      const urlParams = new URLSearchParams(window.location.search)
      const code = urlParams.get('code')
      const error = urlParams.get('error')
      const authError = urlParams.get('auth_error')

      // Handle errors
      if (authError || error) {
        const errorMessage = authError ? decodeURIComponent(authError) : error
        console.error('OAuth error:', errorMessage)
        alert(`Authentication failed: ${errorMessage}`)
        window.history.replaceState({}, document.title, window.location.pathname)
        return
      }

      // Exchange code for session
      if (code) {
        try {
          console.log('Processing OAuth code...')
          const { error: exchangeError } = await supabase.auth.exchangeCodeForSession(code)
          if (exchangeError) {
            console.error('Session exchange error:', exchangeError)
            alert(`Authentication failed: ${exchangeError.message}`)
          }
        } catch (e) {
          console.error('Exchange error:', e)
          alert(`Authentication failed: ${e instanceof Error ? e.message : 'Unknown error'}`)
        } finally {
          window.history.replaceState({}, document.title, window.location.pathname)
        }
      }
    }

    handleAuthCallback()
    
    ;(async () => {
      const { data } = await supabase.auth.getSession()
      if (isMounted) {
        const sessionUser = data.session?.user ?? null
        setUser(sessionUser)
        if (sessionUser) {
          const profile = await checkUserProfile(sessionUser)
          setCurrentView(profile ? "dashboard" : "onboarding")
        } else {
          setCurrentView("landing")
        }
      }
    })()
    
    const { data: authListener } = supabase.auth.onAuthStateChange(async (event, session) => {
      console.log('Auth state changed:', event, session?.user?.email)
      const sessionUser = session?.user ?? null
      setUser(sessionUser)
      if (sessionUser) {
        const profile = await checkUserProfile(sessionUser)
        setCurrentView(profile ? "dashboard" : "onboarding")
      } else {
        setCurrentView("landing")
      }
      setAuthLoading(false)
    })
    
    return () => {
      authListener.subscription.unsubscribe()
      isMounted = false
    }
  }, [])

  // Convert numeric preferences (1-5) to string levels expected by matching API
  const intToPreference = (value: number | null | undefined) => {
    if (!value) return 'MEDIUM'
    if (value <= 1) return 'VERY_LOW'
    if (value === 2) return 'LOW'
    if (value === 3) return 'MEDIUM'
    if (value === 4) return 'HIGH'
    return 'VERY_HIGH'
  }

  // Refresh roommate matches from saved profile
  const refreshMatchesFromProfile = async () => {
    try {
      const { data } = await supabase.auth.getSession()
      const token = data.session?.access_token
      if (!token) return

      const profile = await checkUserProfile(data.session?.user ?? null)
      if (!profile?.id) return

      const roommateMatchingData = {
        name: profile.name,
        email: data.session?.user?.email || '',
        budget_min: profile.budget,
        budget_max: profile.budget + 200,
        preferred_bedrooms: profile.preferred_bedrooms || 2,
        cleanliness: intToPreference(profile.cleanliness),
        noise_level: intToPreference(profile.noise),
        study_time: intToPreference(profile.study_time),
        social_level: intToPreference(profile.social),
        sleep_schedule: intToPreference(profile.sleep),
        pet_friendly: false,
        smoking: false,
        year: profile.year,
        major: profile.major || 'Undeclared',
        min_compatibility: 0.5,
      }

      const matchesResp = await fetch(`${process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000'}/matching/roommate-matches`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(roommateMatchingData),
      })

      if (matchesResp.ok) {
        const matchesData = await matchesResp.json()
        setRoommateMatches(matchesData.matches || [])
      }
    } catch (e) {
      console.error('Failed to refresh roommate matches from profile', e)
    }
  }

  // Auto-refresh matches whenever user lands on dashboard
  useEffect(() => {
    if (currentView === 'dashboard' && user) {
      refreshMatchesFromProfile()
    }
  }, [currentView, user])

  const signInWithGoogle = async () => {
    if (authLoading) return // Prevent multiple simultaneous sign-in attempts

    try {
      setAuthLoading(true)
      console.log('Starting Google OAuth...')

      const { error } = await supabase.auth.signInWithOAuth({
        provider: 'google',
        options: {
          redirectTo: `${window.location.origin}/auth/callback`,
          queryParams: {
            prompt: 'select_account',
            access_type: 'offline'
          }
        },
      })

      if (error) {
        console.error('OAuth initialization failed:', error)
        alert(`Sign-in failed: ${error.message}`)
        setAuthLoading(false)
      }
      // Note: Don't set loading to false here since we're redirecting to Google
    } catch (e) {
      console.error('Unexpected sign-in error:', e)
      alert(`Sign-in failed: ${e instanceof Error ? e.message : 'Unknown error'}`)
      setAuthLoading(false)
    }
  }

  const signOut = async () => {
    if (authLoading) return
    setAuthLoading(true)
    const signOutWithTimeout = async (ms: number) => {
      return Promise.race([
        supabase.auth.signOut(),
        new Promise((_, reject) => setTimeout(() => reject(new Error('timeout')), ms)),
      ])
    }
    try {
      await signOutWithTimeout(5000)
    } catch (e) {
      console.warn('Global sign-out failed or timed out. Falling back to local sign-out.', e)
      try {
        await supabase.auth.signOut({ scope: 'local' })
      } catch (err) {
        console.error('Local sign-out also failed', err)
      }
    } finally {
      setUser(null)
      setRoommateMatches([])
      setCurrentView("landing")
      setAuthLoading(false)
    }
  }

  const toggleDarkMode = () => {
    setDarkMode(!darkMode)
    document.documentElement.classList.toggle("dark")
  }

  // Submit onboarding → create profile in backend and find roommate matches
  const createProfile = async () => {
    try {
      const { data } = await supabase.auth.getSession()
      const token = data.session?.access_token
      if (!token) {
        alert('You need to sign in first. Please use the "Sign in with Google" button to authenticate.')
        return
      }

      const name = (document.getElementById('name') as HTMLInputElement | null)?.value?.trim() || ''
      const year = selectedYear || 'Junior'
      const major = (document.getElementById('major') as HTMLInputElement | null)?.value?.trim() || 'Computer Science'
      const budgetStr = (document.getElementById('budget') as HTMLInputElement | null)?.value || '1000'
      const budget = Number(String(budgetStr).replace(/[^0-9]/g, '')) || 1000
      const moveInVal = (document.getElementById('moveIn') as HTMLInputElement | null)?.value || ''
      const move_in = moveInVal ? moveInVal : null

      // Convert slider values to preference strings for roommate matching
      const convertPreference = (value: number) => {
        if (value <= 1) return 'VERY_LOW'
        if (value <= 2) return 'LOW'
        if (value <= 3) return 'MEDIUM'
        if (value <= 4) return 'HIGH'
        return 'VERY_HIGH'
      }

      // Convert slider values to integers (1-5) for Supabase profiles table
      const convertPreferenceToInt = (value: number) => {
        if (value <= 1) return 1
        if (value <= 2) return 2
        if (value <= 3) return 3
        if (value <= 4) return 4
        return 5
      }

      // First, create/update the user's profile in the Supabase profiles table via backend
      const profilesPayload = {
        name,
        year,
        major,
        budget,
        move_in,
        tags: [],
        cleanliness: convertPreferenceToInt(preferences.cleanliness[0]),
        noise: convertPreferenceToInt(preferences.noiseLevel[0]),
        study_time: convertPreferenceToInt(preferences.studyTime[0]),
        social: convertPreferenceToInt(preferences.socialLevel[0]),
        sleep: convertPreferenceToInt(preferences.sleepSchedule[0])
      }

      const profilesResp = await fetch(`${process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000'}/profiles`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify(profilesPayload),
      })

      if (!profilesResp.ok) {
        const text = await profilesResp.text()
        console.error('Failed to create profile in Supabase profiles table:', text)
        
        // Handle authentication errors specifically
        if (profilesResp.status === 401) {
          alert('Your session has expired. Please sign in again using the "Sign in with Google" button.')
          return
        }
        
        alert(`Failed to create profile (profiles table): ${text}`)
        return
      }

      const createdProfile = await profilesResp.json()
      console.log('Profile created in Supabase (profiles table):', createdProfile)

      // Use the roommate-preferences endpoint which stores profile data for matching
      const roommateProfileData = {
        name,
        email: data.session?.user?.email || '',
        budget_min: budget,
        budget_max: budget + 200,
        preferred_bedrooms: preferredBedrooms,
        cleanliness: convertPreference(preferences.cleanliness[0]),
        noise_level: convertPreference(preferences.noiseLevel[0]),
        study_time: convertPreference(preferences.studyTime[0]),
        social_level: convertPreference(preferences.socialLevel[0]),
        sleep_schedule: convertPreference(preferences.sleepSchedule[0]),
        pet_friendly: false,
        smoking: false,
        year,
        major,
        max_distance_to_vt: maxDistanceToVt,
        preferred_amenities: preferredAmenities
      }

      let resp = await fetch(`${process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000'}/matching/roommate-preferences`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(roommateProfileData),
      })

      if (!resp.ok) {
        const text = await resp.text()
        alert(`Failed to create profile: ${text}`)
        return
      }

      if (resp.ok) {
        const profileData = await resp.json()
        console.log('Profile created in Supabase:', profileData)
        
        // Now find roommate matches using the same data
        const roommateMatchingData = {
          ...roommateProfileData,
          min_compatibility: 0.5
        }

        // Find roommate matches
        const matchesResp = await fetch(`${process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000'}/matching/roommate-matches`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(roommateMatchingData),
        })

        if (matchesResp.ok) {
          const matchesData = await matchesResp.json()
          console.log('Found roommate matches:', matchesData)
          setRoommateMatches(matchesData.matches || []) // Store the matches
        }
      } else {
        const text = await resp.text()
        alert(`Failed to create profile: ${text}`)
        return
      }

      alert('Profile created successfully! Finding your perfect roommate matches...')
      setActiveTab('roommates') // Set to roommates tab
      setCurrentView('dashboard')
    } catch (e) {
      console.error('createProfile failed', e)
      alert('Failed to create profile. Please try again.')
    }
  }

  // Mock data
  const roommates = [
    {
      id: 1,
      name: "Sarah Chen",
      major: "Computer Science",
      year: "Junior",
      photo: "/person-placeholder-1.png",
      compatibility: 92,
      matchingPrefs: ["Clean", "Quiet", "Early Bird"],
    },
    {
      id: 2,
      name: "Mike Johnson",
      major: "Engineering",
      year: "Sophomore",
      photo: "/person-placeholder-2.png",
      compatibility: 87,
      matchingPrefs: ["Social", "Study Groups", "Night Owl"],
    },
    {
      id: 3,
      name: "Emma Davis",
      major: "Business",
      year: "Senior",
      photo: "/person-placeholder-3.png",
      compatibility: 84,
      matchingPrefs: ["Organized", "Moderate Social", "Balanced"],
    },
  ]

  // Format apartments for display
  const properties = apartments.map(apartment => formatApartmentForDisplay(apartment))

  const requestLatestInfoCall = async (propertyId: string) => {
    try {
      setCallingPropertyId(propertyId)

      // Get user profile data
      const { data } = await supabase.auth.getSession()
      const profile = await checkUserProfile(data.session?.user ?? null)

      // Find the selected property
      const selectedProperty = properties.find(p => p.id === propertyId)

      // Prepare user context for the voice agent
      const userContext = {
        user_preferences: profile ? {
          name: profile.name,
          budget: profile.budget,
          year: profile.year,
          major: profile.major,
          cleanliness: profile.cleanliness,
          noise_level: profile.noise,
          study_time: profile.study_time,
          social_level: profile.social,
          sleep_schedule: profile.sleep
        } : null,
        apartment_info: selectedProperty ? {
          name: selectedProperty.name,
          address: selectedProperty.address,
          price: selectedProperty.price,
          bedrooms: selectedProperty.bedrooms,
          distance: selectedProperty.distance,
          lease_type: selectedProperty.leaseType,
          pets: selectedProperty.pets,
          parking: selectedProperty.parking,
          amenities: selectedProperty.furniture + ', ' + selectedProperty.laundry + ', ' + selectedProperty.utilities
        } : null
      }

      const resp = await fetch(`${process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000'}/voice/call`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          to_number: '+16505056094',
          user_context: userContext
        }),
      })
      if (!resp.ok) {
        const text = await resp.text()
        throw new Error(text || 'Failed to initiate call')
      }
      alert('Calling you now with our housing agent to get the latest info...')
    } catch (e) {
      console.error('Failed to start voice call', e)
      alert('Could not place the call. Please try again in a moment.')
    } finally {
      setCallingPropertyId(null)
    }
  }

  const getHousingMatchClass = (percentage: number) => {
    if (percentage >= 80) return "bg-green-100 text-green-700 border-green-200"
    if (percentage >= 60) return "bg-yellow-100 text-yellow-700 border-yellow-200"
    return "bg-red-100 text-red-700 border-red-200"
  }

  // Fetch apartment compatibility for Browse Housing when user switches to that tab
  useEffect(() => {
    if (activeTab !== 'housing' || !user) return
    ;(async () => {
      try {
        const profile = await checkUserProfile(user)
        if (!profile?.id) return
        const resp = await fetch(`${process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000'}/matching/apartment-matches/${profile.id}?limit=100`)
        if (!resp.ok) return
        const data = await resp.json()
        const map: Record<string, { match_percentage: number; reasons: string[] }> = {}
        for (const m of (data.matches || [])) {
          map[m.apartment_name] = {
            match_percentage: m.match_percentage,
            reasons: m.reasons || []
          }
        }
        setHousingMatches(map)
      } catch (e) {
        console.error('Failed to fetch housing compatibility', e)
      }
    })()
  }, [activeTab, user])

  if (currentView === "landing") {
    return (
      <div className="min-h-screen bg-background">
        <nav className="sticky top-0 z-50 border-b border-border bg-background/80 backdrop-blur-md supports-[backdrop-filter]:bg-background/60">
          <div className="max-w-6xl mx-auto px-6 lg:px-8">
            <div className="flex justify-between items-center h-16">
              <div className="flex items-center">
                <h1 className="text-2xl font-bold tracking-tight">HokieNest</h1>
              </div>
              <div className="flex items-center gap-4">
                <Button variant="ghost" size="sm" onClick={toggleDarkMode} className="w-9 h-9 p-0">
                  {darkMode ? <Sun className="h-4 w-4" /> : <Moon className="h-4 w-4" />}
                </Button>
                {user ? (
                  <Button variant="outline" onClick={() => setCurrentView("dashboard")}>Dashboard</Button>
                ) : (
                  <Button
                    variant="outline"
                    onClick={signInWithGoogle}
                    disabled={authLoading}
                  >
                    {authLoading ? 'Signing in...' : 'Sign in with Google'}
                  </Button>
                )}
              </div>
            </div>
          </div>
        </nav>

        <main className="max-w-6xl mx-auto px-6 lg:px-8">
          <div className="py-32 text-center">
            <h1 className="text-6xl font-bold tracking-tight text-balance mb-8 leading-tight">
              Find Your Perfect
              <br />
              <span className="text-primary">Roommate & Home</span>
              <br />
              at Virginia Tech
            </h1>
            <p className="text-xl text-muted-foreground mb-16 max-w-2xl mx-auto text-pretty leading-relaxed">
              Connect with compatible roommates and discover the best housing options near campus with our intelligent
              matching system.
            </p>

            <div className="flex flex-col sm:flex-row gap-6 justify-center">
              <Button
                size="lg"
                className="text-lg px-10 py-6 h-auto font-medium shadow-lg hover:shadow-xl transition-all duration-150"
                onClick={() => (user ? setCurrentView("dashboard") : signInWithGoogle())}
                disabled={authLoading}
              >
                {user ? "Go to Dashboard" : authLoading ? "Signing in..." : "Find Roommates"}
              </Button>
              <Button
                size="lg"
                variant="outline"
                className="text-lg px-10 py-6 h-auto font-medium bg-transparent"
                onClick={() => setCurrentView("dashboard")}
              >
                Browse Housing
              </Button>
            </div>
          </div>
        </main>
      </div>
    )
  }

  if (currentView === "onboarding") {
    // Check if user is authenticated before showing onboarding
    if (!user) {
      return (
        <div className="min-h-screen bg-background flex items-center justify-center">
          <div className="text-center">
            <h1 className="text-2xl font-bold mb-4">Authentication Required</h1>
            <p className="text-muted-foreground mb-6">Please sign in to create your profile</p>
            <Button onClick={() => setCurrentView("landing")}>
              Go to Sign In
            </Button>
          </div>
        </div>
      )
    }
    
    return (
      <div className="min-h-screen bg-background">
        <nav className="sticky top-0 z-50 border-b border-border bg-background/80 backdrop-blur-md">
          <div className="max-w-6xl mx-auto px-6 lg:px-8">
            <div className="flex justify-between items-center h-16">
              <h1 className="text-2xl font-bold tracking-tight">HokieNest</h1>
              <div className="flex items-center gap-4">
                <Button variant="ghost" size="sm" onClick={toggleDarkMode} className="w-9 h-9 p-0">
                  {darkMode ? <Sun className="h-4 w-4" /> : <Moon className="h-4 w-4" />}
                </Button>
                <Button variant="ghost" onClick={() => setCurrentView("landing")}>
                  Back
                </Button>
              </div>
            </div>
          </div>
        </nav>

        <main className="max-w-5xl mx-auto px-6 lg:px-8 py-16">
          <div className="text-center mb-16">
            <h1 className="text-5xl font-bold mb-6 tracking-tight">Create Your Profile</h1>
            <p className="text-xl text-muted-foreground">Help us find your perfect roommate match</p>
          </div>

          <Card className="p-12 card-hover border-border/50">
            <div className="grid md:grid-cols-2 gap-16">
              {/* Basic Info */}
              <div className="space-y-8">
                <h2 className="text-3xl font-bold tracking-tight">Basic Information</h2>

                  <div className="space-y-6">
                  <div className="space-y-3">
                    <Label htmlFor="name" className="text-sm font-medium text-foreground">
                      Full Name
                    </Label>
                    <Input
                      id="name"
                      placeholder="Enter your name"
                      className="h-12 border-border/50 bg-input/50 focus:bg-background transition-colors"
                    />
                  </div>

                  <div className="space-y-3">
                    <Label htmlFor="year" className="text-sm font-medium text-foreground">
                      Year
                    </Label>
                    <Select value={selectedYear} onValueChange={setSelectedYear}>
                      <SelectTrigger className="h-12 border-border/50 bg-input/50 focus:bg-background transition-colors">
                        <SelectValue placeholder="Select your year" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="Freshman">Freshman</SelectItem>
                        <SelectItem value="Sophomore">Sophomore</SelectItem>
                        <SelectItem value="Junior">Junior</SelectItem>
                        <SelectItem value="Senior">Senior</SelectItem>
                        <SelectItem value="Graduate">Graduate</SelectItem>
                        <SelectItem value="Other">Other</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>

                  <div className="space-y-3">
                    <Label htmlFor="major" className="text-sm font-medium text-foreground">
                      Major
                    </Label>
                    <Input
                      id="major"
                      placeholder="Computer Science"
                      defaultValue="Computer Science"
                      className="h-12 border-border/50 bg-input/50 focus:bg-background transition-colors"
                    />
                  </div>

                  <div className="space-y-3">
                    <Label htmlFor="budget" className="text-sm font-medium text-foreground">
                      Budget (per month)
                    </Label>
                    <Input
                      id="budget"
                      placeholder="$800"
                      className="h-12 border-border/50 bg-input/50 focus:bg-background transition-colors"
                    />
                  </div>

                  <div className="space-y-3">
                    <Label htmlFor="bedrooms" className="text-sm font-medium text-foreground">
                      Preferred Bedrooms
                    </Label>
                    <Select value={preferredBedrooms.toString()} onValueChange={(value) => setPreferredBedrooms(parseInt(value))}>
                      <SelectTrigger className="h-12 border-border/50 bg-input/50 focus:bg-background transition-colors">
                        <SelectValue placeholder="Select bedroom count" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="1">1 Bedroom</SelectItem>
                        <SelectItem value="2">2 Bedrooms</SelectItem>
                        <SelectItem value="3">3 Bedrooms</SelectItem>
                        <SelectItem value="4">4 Bedrooms</SelectItem>
                        <SelectItem value="5">5 Bedrooms</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>

                  <div className="space-y-3">
                    <Label htmlFor="moveIn" className="text-sm font-medium text-foreground">
                      Move-in Date
                    </Label>
                    <Input
                      id="moveIn"
                      type="date"
                      className="h-12 border-border/50 bg-input/50 focus:bg-background transition-colors"
                    />
                  </div>
                </div>
              </div>

              {/* Preferences */}
              <div className="space-y-8">
                <h2 className="text-3xl font-bold tracking-tight">Quick Preferences</h2>

                <div className="space-y-8">
                  <div className="space-y-4">
                    <Label className="text-sm font-medium text-foreground">Cleanliness Level</Label>
                    <Slider
                      value={preferences.cleanliness}
                      onValueChange={(value) => setPreferences({ ...preferences, cleanliness: value })}
                      max={5}
                      min={1}
                      step={1}
                      className="mt-3"
                    />
                    <div className="flex justify-between text-sm text-muted-foreground mt-2">
                      <span>Relaxed</span>
                      <span>Very Clean</span>
                    </div>
                  </div>

                  <div className="space-y-4">
                    <Label className="text-sm font-medium text-foreground">Noise Level</Label>
                    <Slider
                      value={preferences.noiseLevel}
                      onValueChange={(value) => setPreferences({ ...preferences, noiseLevel: value })}
                      max={5}
                      min={1}
                      step={1}
                      className="mt-3"
                    />
                    <div className="flex justify-between text-sm text-muted-foreground mt-2">
                      <span>Quiet</span>
                      <span>Lively</span>
                    </div>
                  </div>

                  <div className="space-y-4">
                    <Label className="text-sm font-medium text-foreground">Study Time</Label>
                    <Slider
                      value={preferences.studyTime}
                      onValueChange={(value) => setPreferences({ ...preferences, studyTime: value })}
                      max={5}
                      min={1}
                      step={1}
                      className="mt-3"
                    />
                    <div className="flex justify-between text-sm text-muted-foreground mt-2">
                      <span>Light</span>
                      <span>Intensive</span>
                    </div>
                  </div>

                  <div className="space-y-4">
                    <Label className="text-sm font-medium text-foreground">Social Level</Label>
                    <Slider
                      value={preferences.socialLevel}
                      onValueChange={(value) => setPreferences({ ...preferences, socialLevel: value })}
                      max={5}
                      min={1}
                      step={1}
                      className="mt-3"
                    />
                    <div className="flex justify-between text-sm text-muted-foreground mt-2">
                      <span>Private</span>
                      <span>Very Social</span>
                    </div>
                  </div>

                  <div className="space-y-4">
                    <Label className="text-sm font-medium text-foreground">Sleep Schedule</Label>
                    <Slider
                      value={preferences.sleepSchedule}
                      onValueChange={(value) => setPreferences({ ...preferences, sleepSchedule: value })}
                      max={5}
                      min={1}
                      step={1}
                      className="mt-3"
                    />
                    <div className="flex justify-between text-sm text-muted-foreground mt-2">
                      <span>Early Bird</span>
                      <span>Night Owl</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            {/* Location Preferences */}
            <div className="mt-16 pt-12 border-t border-border/50">
              <h2 className="text-3xl font-bold mb-8 tracking-tight">What's important to you?</h2>
              <div className="grid grid-cols-2 md:grid-cols-3 gap-6">
                {["Campus", "Restaurants", "Grocery", "Gym", "Nightlife", "Study Spots"].map((location) => (
                  <div key={location} className="flex items-center space-x-3">
                    <Checkbox id={location} />
                    <Label htmlFor={location} className="text-sm font-medium">
                      {location}
                    </Label>
                  </div>
                ))}
              </div>
            </div>

            {/* Distance and Amenities Preferences */}
            <div className="mt-16 pt-12 border-t border-border/50">
              <h2 className="text-3xl font-bold mb-8 tracking-tight">Apartment Preferences</h2>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                {/* Distance Preference */}
                <div className="space-y-4">
                  <Label htmlFor="max_distance" className="text-lg font-medium">
                    Maximum Distance to VT (miles)
                  </Label>
                  <div className="space-y-3">
                    <Slider
                      value={[maxDistanceToVt]}
                      onValueChange={(value) => setMaxDistanceToVt(value[0])}
                      max={10}
                      min={0.5}
                      step={0.5}
                      className="mt-3"
                    />
                    <div className="flex justify-between text-sm text-muted-foreground mt-2">
                      <span>0.5 miles</span>
                      <span className="font-medium">{maxDistanceToVt} miles</span>
                      <span>10 miles</span>
                    </div>
                  </div>
                </div>

                {/* Amenities Preference */}
                <div className="space-y-4">
                  <Label className="text-lg font-medium">Preferred Amenities</Label>
                  <div className="grid grid-cols-2 gap-3">
                    {["Pool", "Fitness Center", "Laundry", "Parking", "Pet Friendly", "WiFi"].map((amenity) => (
                      <div key={amenity} className="flex items-center space-x-3">
                        <Checkbox
                          id={amenity}
                          checked={preferredAmenities.includes(amenity)}
                          onCheckedChange={(checked) => {
                            if (checked) {
                              setPreferredAmenities([...preferredAmenities, amenity])
                            } else {
                              setPreferredAmenities(preferredAmenities.filter((a: string) => a !== amenity))
                            }
                          }}
                        />
                        <Label htmlFor={amenity} className="text-sm font-medium">
                          {amenity}
                        </Label>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            </div>

            <div className="mt-16 text-center">
              <Button
                size="lg"
                className="px-16 py-6 h-auto text-lg font-medium shadow-lg hover:shadow-xl transition-all duration-150"
                onClick={createProfile}
              >
                Create Profile & Find Roommates
              </Button>
            </div>
          </Card>
        </main>
      </div>
    )
  }

  // Dashboard View
  return (
    <div className="min-h-screen bg-background">
      <nav className="sticky top-0 z-50 border-b border-border bg-background/80 backdrop-blur-md">
        <div className="max-w-6xl mx-auto px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <h1 className="text-2xl font-bold tracking-tight">HokieNest</h1>
            <div className="flex items-center gap-4">
              <Button variant="ghost" size="sm" onClick={toggleDarkMode} className="w-9 h-9 p-0">
                {darkMode ? <Sun className="h-4 w-4" /> : <Moon className="h-4 w-4" />}
              </Button>
              {user ? (
                <Button
                  variant="ghost"
                  onClick={signOut}
                  disabled={authLoading}
                >
                  {authLoading ? 'Signing out...' : 'Sign Out'}
                </Button>
              ) : (
                <Button
                  variant="ghost"
                  onClick={signInWithGoogle}
                  disabled={authLoading}
                >
                  {authLoading ? 'Signing in...' : 'Sign In'}
                </Button>
              )}
            </div>
          </div>
        </div>
      </nav>

      <main className="max-w-6xl mx-auto px-6 lg:px-8 py-12">
        <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
          <TabsList className="grid w-full grid-cols-4 h-12 p-1 bg-muted/50">
            <TabsTrigger value="roommates" className="font-medium">
              Find Roommates
            </TabsTrigger>
            <TabsTrigger value="housing" className="font-medium">
              Browse Housing
            </TabsTrigger>
            <TabsTrigger value="matches" className="font-medium">
              My Matches
            </TabsTrigger>
          </TabsList>

          <TabsContent value="roommates" className="mt-12">
            <div className="flex justify-between items-center mb-8">
              <div>
                <h2 className="text-3xl font-bold mb-2">Your Roommate Matches</h2>
                <p className="text-muted-foreground">
                  {roommateMatches.length > 0 
                    ? `Found ${roommateMatches.length} compatible roommate${roommateMatches.length === 1 ? '' : 's'} based on your preferences`
                    : "No matches yet - complete your profile to find compatible roommates"
                  }
                </p>
              </div>
              {roommateMatches.length > 0 && (
                <Button 
                  variant="outline" 
                  size="sm"
                  onClick={() => {
                    setRoommateMatches([])
                    setApartmentMatches([])
                  }}
                >
                  Find New Matches
                </Button>
              )}
            </div>

            {roommateMatches.length === 0 ? (
              <div className="text-center py-16">
                <div className="mb-8">
                  <Heart className="h-16 w-16 mx-auto text-muted-foreground/50 mb-4" />
                  <h3 className="text-xl font-semibold mb-2">No matches yet</h3>
                  <p className="text-muted-foreground mb-6">
                    Complete your profile through the onboarding process to find compatible roommates!
                  </p>
                  <Button 
                    size="lg" 
                    className="gap-2"
                    onClick={() => setActiveTab("roommates")}
                  >
                    <Heart className="h-5 w-5" />
                    Find Roommates
                  </Button>
                </div>
              </div>
            ) : (
              <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
                {roommateMatches.map((match) => (
                  <Card key={match.id} className="p-8 card-hover border-border/50">
                    <div className="text-center">
                      <img
                        src={`https://picsum.photos/200/200?random=${Math.abs(match.name.split('').reduce((a,b) => a + b.charCodeAt(0), 0)) % 1000}`}
                        alt={match.name}
                        className="w-28 h-28 rounded-full mx-auto mb-6 object-cover border-2 border-border/20"
                      />
                      <h3 className="text-xl font-bold mb-2 tracking-tight">{match.name}</h3>
                      <p className="text-muted-foreground mb-4 text-sm">
                        {match.major} • {match.year}
                      </p>

                      <Badge
                        variant="secondary"
                        className={`text-lg font-bold mb-6 px-4 py-2 ${
                          match.compatibility_percentage >= 80 
                            ? "bg-green-100 text-green-700 border-green-200" 
                            : match.compatibility_percentage >= 60 
                            ? "bg-yellow-100 text-yellow-700 border-yellow-200"
                            : "bg-red-100 text-red-700 border-red-200"
                        }`}
                      >
                        {match.compatibility_percentage}% Match
                      </Badge>

                      <div className="space-y-2 mb-6 text-sm">
                        <div className="flex justify-between">
                          <span className="text-muted-foreground">Budget:</span>
                          <span className="font-medium">${match.budget}/month</span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-muted-foreground">Cleanliness:</span>
                          <span className="font-medium">{match.preferences.cleanliness}/5</span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-muted-foreground">Noise Level:</span>
                          <span className="font-medium">{match.preferences.noise_level}/5</span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-muted-foreground">Study Time:</span>
                          <span className="font-medium">{match.preferences.study_time}/5</span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-muted-foreground">Social Level:</span>
                          <span className="font-medium">{match.preferences.social_level}/5</span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-muted-foreground">Sleep Schedule:</span>
                          <span className="font-medium">{match.preferences.sleep_schedule}/5</span>
                        </div>
                      </div>

                      <div className="flex gap-3">
                        <Button
                          className="flex-1 gap-2 h-11 font-medium"
                          onClick={() => window.open('https://instagram.com', '_blank')}
                        >
                          <ExternalLink className="h-4 w-4" />
                          Contact
                        </Button>
                        <Button variant="outline" className="gap-2 h-11 font-medium">
                          <Heart className="h-4 w-4" />
                          Like
                        </Button>
                      </div>
                    </div>
                  </Card>
                ))}
              </div>
            )}

            {/* Apartment Matches Section */}
            {apartmentMatches.length > 0 && (
              <div className="mt-16 pt-12 border-t border-border/50">
                <div className="flex justify-between items-center mb-8">
                  <div>
                    <h3 className="text-2xl font-bold mb-2">Your Apartment Matches</h3>
                    <p className="text-muted-foreground">
                      Found {apartmentMatches.length} apartment{apartmentMatches.length === 1 ? '' : 's'} that match your preferences
                    </p>
                  </div>
                  <Button 
                    variant="outline" 
                    size="sm"
                    onClick={() => setApartmentMatches([])}
                  >
                    Clear Results
                  </Button>
                </div>

                <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
                  {apartmentMatches.map((match, index) => (
                    <Card key={index} className="p-6 card-hover border-border/50">
                      <div className="space-y-4">
                        <div className="flex justify-between items-start">
                          <div>
                            <h4 className="font-bold text-lg">{match.apartment_name}</h4>
                            <p className="text-sm text-muted-foreground">{match.apartment_address}</p>
                          </div>
                          <Badge 
                            variant={match.match_percentage >= 70 ? "default" : match.match_percentage >= 50 ? "secondary" : "destructive"}
                            className="text-xs"
                          >
                            {match.match_percentage}% match
                          </Badge>
                        </div>

                        <div className="space-y-2 text-sm">
                          <div className="flex justify-between">
                            <span className="text-muted-foreground">Price:</span>
                            <span className="font-medium">{match.price}</span>
                          </div>
                          <div className="flex justify-between">
                            <span className="text-muted-foreground">Bedrooms:</span>
                            <span className="font-medium">{match.bedroom_count}</span>
                          </div>
                          <div className="flex justify-between">
                            <span className="text-muted-foreground">Distance to VT:</span>
                            <span className="font-medium">{match.distance_to_vt} miles</span>
                          </div>
                          {match.amenities && match.amenities.length > 0 && (
                            <div>
                              <span className="text-muted-foreground">Amenities:</span>
                              <div className="flex flex-wrap gap-1 mt-1">
                                {match.amenities.slice(0, 3).map((amenity, i) => (
                                  <Badge key={i} variant="outline" className="text-xs">
                                    {amenity}
                                  </Badge>
                                ))}
                                {match.amenities.length > 3 && (
                                  <Badge variant="outline" className="text-xs">
                                    +{match.amenities.length - 3} more
                                  </Badge>
                                )}
                              </div>
                            </div>
                          )}
                        </div>

                        {match.reasons && match.reasons.length > 0 && (
                          <div className="space-y-1">
                            <p className="text-xs text-muted-foreground font-medium">Why it matches:</p>
                            {match.reasons.slice(0, 2).map((reason, i) => (
                              <p key={i} className="text-xs text-muted-foreground">• {reason}</p>
                            ))}
                          </div>
                        )}

                        <Button className="w-full gap-2">
                          <ExternalLink className="h-4 w-4" />
                          View Details
                        </Button>
                      </div>
                    </Card>
                  ))}
                </div>
              </div>
            )}
          </TabsContent>

          <TabsContent value="housing" className="mt-12">
            <div className="space-y-8">
              {apartmentsLoading ? (
                <div className="flex items-center justify-center py-12">
                  <Loader2 className="h-8 w-8 animate-spin" />
                  <span className="ml-2">Loading apartments...</span>
                </div>
              ) : apartmentsError ? (
                <div className="text-center py-12">
                  <AlertCircle className="h-12 w-12 mx-auto text-red-500 mb-4" />
                  <p className="text-red-500">Error loading apartments: {apartmentsError}</p>
                </div>
              ) : properties.length === 0 ? (
                <div className="text-center py-12">
                  <Home className="h-12 w-12 mx-auto text-muted-foreground mb-4" />
                  <p className="text-muted-foreground">No apartments found</p>
                </div>
              ) : (
                properties.map((property) => (
                <Card key={property.id} className="p-8 card-hover border-border/50">
                  <div className="flex gap-8">
                    <img
                      src={property.imageUrl || `https://picsum.photos/800/600?random=${Math.abs(property.name.split('').reduce((a,b) => a + b.charCodeAt(0), 0)) % 1000}`}
                      alt={property.name}
                      className="w-56 h-40 rounded-lg object-cover border border-border/20"
                    />
                    <div className="flex-1">
                      <div className="flex justify-between items-start mb-4">
                        <div className="flex items-center gap-3">
                          <h3 className="text-2xl font-bold tracking-tight">{property.name}</h3>
                          {housingMatches[property.name] && (
                            <Badge
                              variant="secondary"
                              className={`text-sm font-semibold ${getHousingMatchClass(housingMatches[property.name].match_percentage)}`}
                            >
                              {housingMatches[property.name].match_percentage}% Match
                            </Badge>
                          )}
                        </div>
                        <div className="flex flex-col items-end gap-2">
                          <span className="text-3xl font-bold text-primary">{property.price}</span>
                          {property.price === 'Contact for pricing' && (
                            <Button
                              variant="outline"
                              size="sm"
                              className="h-9 font-medium"
                              onClick={() => requestLatestInfoCall(property.id)}
                              disabled={callingPropertyId === property.id}
                            >
                              {callingPropertyId === property.id ? (
                                <span className="flex items-center gap-2"><Loader2 className="h-4 w-4 animate-spin" /> Calling…</span>
                              ) : (
                                <span className="flex items-center gap-2"><Phone className="h-4 w-4" /> Get the latest information</span>
                              )}
                            </Button>
                          )}
                        </div>
                      </div>

                      <p className="text-muted-foreground mb-4 text-lg">
                        {property.bedrooms} • {property.address}
                      </p>

                      <div className="flex items-center gap-6 mb-6">
                        <div className="flex items-center gap-2">
                          <MapPin className="h-4 w-4 text-muted-foreground" />
                          <span className="text-sm">{property.distance}</span>
                        </div>
                        <div className="flex items-center gap-2">
                          {property.busStop ? (
                            <CheckCircle className="h-4 w-4 text-green-500" />
                          ) : (
                            <XCircle className="h-4 w-4 text-red-500" />
                          )}
                          <span className="text-sm font-medium">{property.busStop || 'No bus stop'}</span>
                        </div>
                      </div>

                      <Dialog>
                        <DialogTrigger asChild>
                          <Button
                            onClick={() => setSelectedProperty(property)}
                            className="h-11 px-8 font-medium shadow-md hover:shadow-lg transition-all duration-150"
                          >
                            View Details
                          </Button>
                        </DialogTrigger>
                        <DialogContent className="max-w-3xl backdrop-blur-md bg-background/95">
                          <DialogHeader>
                          <DialogTitle className="text-2xl font-bold flex items-center gap-3">
                            {property.name}
                            {housingMatches[property.name] && (
                              <Badge
                                variant="secondary"
                                className={`text-sm font-semibold ${getHousingMatchClass(housingMatches[property.name].match_percentage)}`}
                              >
                                {housingMatches[property.name].match_percentage}% Match
                              </Badge>
                            )}
                          </DialogTitle>
                          </DialogHeader>
                          <div className="space-y-8">
                            <img
                              src={property.imageUrl || `https://picsum.photos/800/600?random=${Math.abs(property.name.split('').reduce((a,b) => a + b.charCodeAt(0), 0)) % 1000}`}
                              alt={property.name}
                              className="w-full h-80 rounded-lg object-cover border border-border/20"
                            />

                            <div className="grid grid-cols-2 gap-8">
                              <div>
                                <h4 className="font-bold mb-4 text-lg">Details</h4>
                                <div className="space-y-2 text-sm">
                                  <p>
                                    <span className="font-medium">Price:</span> {property.price}
                                  </p>
                                  <p>
                                    <span className="font-medium">Bedrooms:</span> {property.bedrooms}
                                  </p>
                                  <p>
                                    <span className="font-medium">Address:</span> {property.address}
                                  </p>
                                  <p>
                                    <span className="font-medium">Distance:</span> {property.distance}
                                  </p>
                                  <p>
                                    <span className="font-medium">Lease Type:</span> {property.leaseType}
                                  </p>
                                  <p>
                                    <span className="font-medium">Lease Term:</span> {property.leaseTerm}
                                  </p>
                                </div>
                              </div>

                              <div>
                                <h4 className="font-bold mb-4 text-lg">Amenities & Features</h4>
                                <div className="space-y-2">
                                  <p className="text-sm">
                                    <span className="font-medium">Pets:</span> {property.pets}
                                  </p>
                                  <p className="text-sm">
                                    <span className="font-medium">Parking:</span> {property.parking}
                                  </p>
                                  <p className="text-sm">
                                    <span className="font-medium">Furniture:</span> {property.furniture}
                                  </p>
                                  <p className="text-sm">
                                    <span className="font-medium">Laundry:</span> {property.laundry}
                                  </p>
                                  <p className="text-sm">
                                    <span className="font-medium">Utilities:</span> {property.utilities}
                                  </p>
                                  <p className="text-sm">
                                    <span className="font-medium">Bus Stop:</span> {property.busStop}
                                  </p>
                                </div>
                              </div>
                            </div>

                            <div className="grid grid-cols-2 gap-8">
                              <div>
                                <h4 className="font-bold mb-4 text-lg">Contact & Fees</h4>
                                <div className="space-y-2 text-sm">
                                  <p>
                                    <span className="font-medium">Phone:</span> {property.phone}
                                  </p>
                                  <p>
                                    <span className="font-medium">Application Fee:</span> {property.applicationFee}
                                  </p>
                                  <p>
                                    <span className="font-medium">Security Deposit:</span> {property.securityDeposit}
                                  </p>
                                  <p>
                                    <span className="font-medium">Additional Fees:</span> {property.additionalFees}
                                  </p>
                                </div>
                              </div>

                              <div>
                                <h4 className="font-bold mb-4 text-lg">Notes</h4>
                                <div className="space-y-2">
                                  <p className="text-sm text-muted-foreground">
                                    {property.notes || 'No additional notes available'}
                                  </p>
                                </div>
                              </div>
                            </div>

                            {housingMatches[property.name]?.reasons?.length ? (
                              <div>
                                <h4 className="font-bold mb-4 text-lg">Why this matches you</h4>
                                <ul className="list-disc list-inside text-sm text-muted-foreground">
                                  {housingMatches[property.name].reasons.map((r, i) => (
                                    <li key={i}>{r}</li>
                                  ))}
                                </ul>
                              </div>
                            ) : null}

                            <div className="flex gap-4">
                              <Button className="flex-1 gap-2 h-12 font-medium shadow-md hover:shadow-lg transition-all duration-150">
                                <Heart className="h-4 w-4" />
                                Save
                              </Button>
                              <Button variant="outline" className="flex-1 h-12 font-medium bg-transparent">
                                Share with Roommates
                              </Button>
                            </div>
                          </div>
                        </DialogContent>
                      </Dialog>
                    </div>
                  </div>
                </Card>
                ))
              )}
            </div>
          </TabsContent>


          <TabsContent value="matches" className="mt-12">
            <div className="space-y-12">
              <div>
                <h2 className="text-3xl font-bold mb-8 tracking-tight">Your Connections</h2>
                <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
                  {roommates.slice(0, 2).map((roommate) => (
                    <Card key={roommate.id} className="p-6 card-hover border-border/50">
                      <div className="flex items-center gap-4">
                        <img
                          src={roommate.photo || "/placeholder.svg"}
                          alt={roommate.name}
                          className="w-16 h-16 rounded-full object-cover border-2 border-border/20"
                        />
                        <div>
                          <h3 className="font-bold text-lg">{roommate.name}</h3>
                          <p className="text-sm text-muted-foreground">{roommate.major}</p>
                        </div>
                      </div>
                    </Card>
                  ))}
                </div>
              </div>

              <div>
                <h2 className="text-3xl font-bold mb-8 tracking-tight">Form a Group</h2>
                <Card className="p-8 card-hover border-border/50">
                  <p className="text-muted-foreground mb-6 text-lg leading-relaxed">
                    Drag profiles together to form a roommate group and find housing together.
                  </p>
                  <Button className="w-full h-12 font-medium" disabled>
                    Find Housing for Group
                  </Button>
                </Card>
              </div>
            </div>
          </TabsContent>
        </Tabs>
      </main>
    </div>
  )
}
