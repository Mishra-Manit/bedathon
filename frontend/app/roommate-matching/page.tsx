'use client'

import { useState, useEffect } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Badge } from "@/components/ui/badge"
import { Checkbox } from "@/components/ui/checkbox"

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
}

const PREFERENCE_LEVELS = [
  { value: 'VERY_LOW', label: 'Very Low' },
  { value: 'LOW', label: 'Low' },
  { value: 'MEDIUM', label: 'Medium' },
  { value: 'HIGH', label: 'High' },
  { value: 'VERY_HIGH', label: 'Very High' }
]

export default function RoommateMatchingPage() {
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
    major: 'Computer Science'
  })

  const [roommateMatches, setRoommateMatches] = useState<RoommateMatch[]>([])
  const [apartmentMatches, setApartmentMatches] = useState<ApartmentMatch[]>([])
  const [loading, setLoading] = useState(false)
  const [activeTab, setActiveTab] = useState('profile')

  const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

  const createProfile = async () => {
    setLoading(true)
    try {
      const response = await fetch(`${API_BASE_URL}/matching/roommate-preferences`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(profile),
      })

      if (response.ok) {
        const result = await response.json()
        setCurrentProfileId(result.profile.id)
        alert('Profile created successfully!')
        setActiveTab('matches')
        // Auto-fetch matches after creating profile
        await fetchRoommateMatches()
        await fetchApartmentMatches()
      } else {
        const error = await response.json()
        alert(`Error: ${error.detail || 'Failed to create profile'}`)
      }
    } catch (error) {
      alert(`Error: ${error}`)
    } finally {
      setLoading(false)
    }
  }

  const fetchRoommateMatches = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/matching/roommate-matches`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ min_compatibility: 0.5 }),
      })

      if (response.ok) {
        const data = await response.json()
        setRoommateMatches(data.matches)
      }
    } catch (error) {
      console.error('Error fetching roommate matches:', error)
    }
  }

  const [currentProfileId, setCurrentProfileId] = useState<string>('')

  const fetchApartmentMatches = async () => {
    if (!currentProfileId) return

    try {
      const response = await fetch(`${API_BASE_URL}/matching/apartment-matches/${currentProfileId}?limit=5`)

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
    <div className="container mx-auto px-4 py-8 max-w-6xl">
      <div className="mb-8">
        <h1 className="text-4xl font-bold text-center mb-4">🏠 Roommate Matching System</h1>
        <p className="text-center text-gray-600 max-w-2xl mx-auto">
          Find compatible roommates and perfect apartments based on your lifestyle preferences and budget.
        </p>
      </div>

      <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
        <TabsList className="grid w-full grid-cols-3">
          <TabsTrigger value="profile">Create Profile</TabsTrigger>
          <TabsTrigger value="matches">Roommate Matches</TabsTrigger>
          <TabsTrigger value="apartments">Apartment Matches</TabsTrigger>
        </TabsList>

        <TabsContent value="profile" className="mt-6">
          <Card>
            <CardHeader>
              <CardTitle>Create Your Roommate Profile</CardTitle>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="space-y-2">
                  <Label htmlFor="name">Name</Label>
                  <Input
                    id="name"
                    value={profile.name || ''}
                    onChange={(e) => setProfile({ ...profile, name: e.target.value })}
                    placeholder="Your full name"
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="email">Email</Label>
                  <Input
                    id="email"
                    type="email"
                    value={profile.email || ''}
                    onChange={(e) => setProfile({ ...profile, email: e.target.value })}
                    placeholder="your.email@vt.edu"
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="budget_min">Minimum Budget ($/month)</Label>
                  <Input
                    id="budget_min"
                    type="number"
                    value={profile.budget_min || ''}
                    onChange={(e) => setProfile({ ...profile, budget_min: parseInt(e.target.value) })}
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="budget_max">Maximum Budget ($/month)</Label>
                  <Input
                    id="budget_max"
                    type="number"
                    value={profile.budget_max || ''}
                    onChange={(e) => setProfile({ ...profile, budget_max: parseInt(e.target.value) })}
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="bedrooms">Preferred Bedrooms</Label>
                  <Select
                    value={profile.preferred_bedrooms?.toString() || '2'}
                    onValueChange={(value) => setProfile({ ...profile, preferred_bedrooms: parseInt(value) })}
                  >
                    <SelectTrigger>
                      <SelectValue />
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
                    value={profile.year || 'Junior'}
                    onValueChange={(value) => setProfile({ ...profile, year: value })}
                  >
                    <SelectTrigger>
                      <SelectValue />
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
                    value={profile.major || ''}
                    onChange={(e) => setProfile({ ...profile, major: e.target.value })}
                    placeholder="Your major"
                  />
                </div>

                <div className="space-y-2">
                  <Label>Cleanliness Level</Label>
                  <Select
                    value={profile.cleanliness || 'MEDIUM'}
                    onValueChange={(value) => setProfile({ ...profile, cleanliness: value })}
                  >
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      {PREFERENCE_LEVELS.map(level => (
                        <SelectItem key={level.value} value={level.value}>
                          {level.label}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>

                <div className="space-y-2">
                  <Label>Noise Tolerance</Label>
                  <Select
                    value={profile.noise_level || 'MEDIUM'}
                    onValueChange={(value) => setProfile({ ...profile, noise_level: value })}
                  >
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      {PREFERENCE_LEVELS.map(level => (
                        <SelectItem key={level.value} value={level.value}>
                          {level.label}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>

                <div className="space-y-2">
                  <Label>Study Time</Label>
                  <Select
                    value={profile.study_time || 'MEDIUM'}
                    onValueChange={(value) => setProfile({ ...profile, study_time: value })}
                  >
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      {PREFERENCE_LEVELS.map(level => (
                        <SelectItem key={level.value} value={level.value}>
                          {level.label}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>

                <div className="space-y-2">
                  <Label>Social Level</Label>
                  <Select
                    value={profile.social_level || 'MEDIUM'}
                    onValueChange={(value) => setProfile({ ...profile, social_level: value })}
                  >
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      {PREFERENCE_LEVELS.map(level => (
                        <SelectItem key={level.value} value={level.value}>
                          {level.label}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>

                <div className="space-y-2">
                  <Label>Sleep Schedule</Label>
                  <Select
                    value={profile.sleep_schedule || 'MEDIUM'}
                    onValueChange={(value) => setProfile({ ...profile, sleep_schedule: value })}
                  >
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      {PREFERENCE_LEVELS.map(level => (
                        <SelectItem key={level.value} value={level.value}>
                          {level.label}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
              </div>

              <div className="flex items-center space-x-6">
                <div className="flex items-center space-x-2">
                  <Checkbox
                    id="pet_friendly"
                    checked={profile.pet_friendly || false}
                    onCheckedChange={(checked) => setProfile({ ...profile, pet_friendly: !!checked })}
                  />
                  <Label htmlFor="pet_friendly">Pet Friendly</Label>
                </div>

                <div className="flex items-center space-x-2">
                  <Checkbox
                    id="smoking"
                    checked={profile.smoking || false}
                    onCheckedChange={(checked) => setProfile({ ...profile, smoking: !!checked })}
                  />
                  <Label htmlFor="smoking">Smoking</Label>
                </div>
              </div>

              <Button 
                onClick={createProfile} 
                disabled={loading || !profile.name || !profile.email}
                className="w-full"
              >
                {loading ? 'Creating Profile...' : 'Create Profile & Find Matches'}
              </Button>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="matches" className="mt-6">
          <div className="space-y-4">
            <div className="flex justify-between items-center">
              <h2 className="text-2xl font-bold">Compatible Roommates</h2>
              <Button onClick={fetchRoommateMatches} variant="outline">
                Refresh Matches
              </Button>
            </div>

            {roommateMatches.length === 0 ? (
              <Card>
                <CardContent className="p-8 text-center">
                  <p className="text-gray-500">No roommate matches found yet. Create your profile first!</p>
                </CardContent>
              </Card>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {roommateMatches.map((match) => (
                  <Card key={match.id}>
                    <CardHeader>
                      <CardTitle className="flex items-center justify-between">
                        <span>{match.name}</span>
                        <Badge className={`${getCompatibilityColor(match.compatibility_percentage)} text-white`}>
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
          </div>
        </TabsContent>

        <TabsContent value="apartments" className="mt-6">
          <div className="space-y-4">
            <div className="flex justify-between items-center">
              <h2 className="text-2xl font-bold">Recommended Apartments</h2>
              <Button onClick={fetchApartmentMatches} variant="outline">
                Refresh Matches
              </Button>
            </div>

            {apartmentMatches.length === 0 ? (
              <Card>
                <CardContent className="p-8 text-center">
                  <p className="text-gray-500">No apartment matches found yet. Create your profile first!</p>
                </CardContent>
              </Card>
            ) : (
              <div className="grid gap-4">
                {apartmentMatches.map((match, index) => (
                  <Card key={index}>
                    <CardContent className="p-6">
                      <div className="flex items-center justify-between mb-4">
                        <h3 className="text-xl font-semibold">{match.apartment_name}</h3>
                        <Badge className={`${getCompatibilityColor(match.match_percentage)} text-white`}>
                          {match.match_percentage}% Match
                        </Badge>
                      </div>

                      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                        <div>
                          <p className="text-sm text-gray-600 mb-2">{match.apartment_address}</p>
                          <div className="space-y-1 text-sm">
                            <p><strong>Price:</strong> {match.price}</p>
                            <p><strong>Bedrooms:</strong> {match.bedroom_count}</p>
                            <p><strong>Distance to VT:</strong> {match.distance_to_vt} miles</p>
                          </div>
                        </div>

                        <div>
                          <h4 className="font-medium mb-2">Amenities</h4>
                          <div className="flex flex-wrap gap-1">
                            {match.amenities.map((amenity, idx) => (
                              <Badge key={idx} variant="secondary" className="text-xs">
                                {amenity}
                              </Badge>
                            ))}
                          </div>
                        </div>
                      </div>

                      <div className="mt-4">
                        <h4 className="font-medium mb-2">Why this apartment matches:</h4>
                        <ul className="text-sm text-gray-600 space-y-1">
                          {match.reasons.map((reason, idx) => (
                            <li key={idx} className="flex items-start">
                              <span className="mr-2">•</span>
                              <span>{reason}</span>
                            </li>
                          ))}
                        </ul>
                      </div>
                    </CardContent>
                  </Card>
                ))}
              </div>
            )}
          </div>
        </TabsContent>
      </Tabs>
    </div>
  )
}
