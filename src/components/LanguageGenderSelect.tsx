import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";

interface LanguageGenderSelectProps {
  onLanguageChange: (value: string) => void;
  onGenderChange: (value: string) => void;
}

export const LanguageGenderSelect = ({ onLanguageChange, onGenderChange }: LanguageGenderSelectProps) => {
  return (
    <div className="flex space-x-4">
      <Select defaultValue="english" onValueChange={onLanguageChange}>
        <SelectTrigger className="w-[140px]">
          <SelectValue placeholder="Select Language" />
        </SelectTrigger>
        <SelectContent>
          <SelectItem value="english">English</SelectItem>
          <SelectItem value="hindi">Hindi</SelectItem>
        </SelectContent>
      </Select>

      <Select defaultValue="male" onValueChange={onGenderChange}>
        <SelectTrigger className="w-[140px]">
          <SelectValue placeholder="Select Gender" />
        </SelectTrigger>
        <SelectContent>
          <SelectItem value="male">Male</SelectItem>
          <SelectItem value="female">Female</SelectItem>
        </SelectContent>
      </Select>
    </div>
  );
}; 