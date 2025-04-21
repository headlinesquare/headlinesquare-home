# check-identity.ps1

# Get your Windows login and machine name
$userName     = $env:USERNAME

# Find any occurrences in all text files
$matches = Get-ChildItem -Recurse -File `
    | Where-Object { $_.Extension -notin '.exe','.dll','.png','.jpg' } `
    | Select-String -Pattern "$userName"

if ($matches) {
    Write-Host "🚨 Detected references to your local identity:" -ForegroundColor Red
    $matches | ForEach-Object {
        "{0}:{1} {2}" -f $_.Path, $_.LineNumber, $_.Line
    }
    exit 1
}

exit 0

