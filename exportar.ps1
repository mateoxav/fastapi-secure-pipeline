<#
.SYNOPSIS
    Exporta todo el código fuente de un directorio de proyecto a un único archivo .txt,
    con un formato amigable para LLMs, excluyendo directorios y archivos no deseados.

.DESCRIPTION
    Este script recorre recursivamente el directorio del proyecto, filtra los
    directorIOS como .git, .venv, node_modules, y extensiones de archivo como .png, .exe,
    y luego concatena el contenido de los archivos restantes en un solo archivo de salida.
    Cada archivo en la salida está precedido por un encabezado "--- File: [ruta/relativa/del/archivo] ---".

.PARAMETER ProjectRoot
    La ruta al directorio raíz del proyecto que deseas exportar.
    Por defecto, es el directorio actual ($PWD).

.PARAMETER OutputFile
    El nombre del archivo .txt de salida que se generará en el ProjectRoot.
    Por defecto es "project_source_export.txt".

.EXAMPLE
    .\Export-ProjectSource.ps1
    (Ejecuta el script en el directorio actual y genera "project_source_export.txt")

.EXAMPLE
    .\Export-ProjectSource.ps1 -ProjectRoot "C:\MisProyectos\MiApp" -OutputFile "MiApp.txt"
    (Ejecuta el script en un directorio específico y genera "MiApp.txt" en esa misma ubicación)
#>
[CmdletBinding()]
param (
    [string]$ProjectRoot = $PWD.Path,
    [string]$OutputFile = "project_source_export.txt"
)

# --- Configuración de Exclusiones ---

# Directorios a ignorar completamente (nombres exactos)
$excludeDirs = @(
    ".git",
    ".vscode",
    ".idea",
    "__pycache__",
    ".venv",
    "dist",
    "build",
    "node_modules",
    ".pytest_cache",
    ".mypy_cache"
     
)

# Extensiones de archivo a ignorar
$excludeExtensions = @(
    # Imágenes
    ".png", ".jpg", ".jpeg", ".gif", ".bmp", ".ico", ".svg",
    # Comprimidos
    ".zip", ".rar", ".gz", ".tar",
    # Binarios y ejecutables
    ".exe", ".dll", ".so", ".a",
    # Documentos
    ".pdf", ".doc", ".docx", ".xls", ".xlsx", ".ppt", ".pptx",
    # Python cache
    ".pyc", ".pyo",
    # Bases de datos
    ".db", ".sqlite3"
)

# Archivos específicos a ignorar
$OutputFullPath = Join-Path $ProjectRoot $OutputFile
$MyScriptName = $MyInvocation.MyCommand.Name
$excludeFiles = @( $OutputFile, $MyScriptName )

# --- Lógica Principal ---

Write-Host "Iniciando la exportación del código fuente..." -ForegroundColor Green
Write-Host "Buscando en: $ProjectRoot"
Write-Host "Archivo de salida: $OutputFullPath"

# Limpiar el archivo de salida si ya existe
if (Test-Path $OutputFullPath) {
    Remove-Item -Path $OutputFullPath -ErrorAction SilentlyContinue
    Write-Host "Archivo de salida anterior eliminado."
}

# Obtener todos los archivos recursivamente
$files = Get-ChildItem -Path $ProjectRoot -Recurse -File

$fileCount = 0

# Procesar cada archivo
$files | ForEach-Object {
    $file = $_
    
    # --- Lógica de Filtro ---
    
    # --- INICIO DE LA CORRECCIÓN ---
    # Calcular la ruta relativa de forma compatible con PS 5.1
    # Reemplazamos la ruta raíz por una cadena vacía, luego quitamos la barra
    # inicial y normalizamos los separadores a '/'
    $relativePath = $file.FullName.Replace($ProjectRoot, "")
    $relativePath = $relativePath.TrimStart("\") -replace "\\", "/"
    # --- FIN DE LA CORRECCIÓN ---

    # 1. Excluir por nombre de archivo específico
    if ($excludeFiles -contains $file.Name) {
        Write-Host "Excluyendo (archivo): $relativePath" -ForegroundColor Gray
        return
    }

    # 2. Excluir por extensión
    if ($excludeExtensions -contains $file.Extension) {
        Write-Host "Excluyendo (extensión): $relativePath" -ForegroundColor Gray
        return
    }

    # 3. Excluir por directorio padre
    $inExcludedDir = $false
    foreach ($dir in $excludeDirs) {
        if ($relativePath.StartsWith("$dir/")) {
            $inExcludedDir = $true
            break
        }
    }
    if ($inExcludedDir) {
        Write-Host "Excluyendo (directorio): $relativePath" -ForegroundColor Gray
        return
    }

    # --- Escritura en el Archivo ---
    
    $fileCount++
    Write-Host "Procesando: $relativePath" -ForegroundColor Cyan
    
    $header = "--- File: $relativePath ---"
    
    # Intentar leer el contenido del archivo
    try {
        $content = Get-Content -Path $file.FullName -Raw -Encoding Default -ErrorAction Stop
    } catch {
        Write-Warning "No se pudo leer el archivo '$relativePath'. Omitiendo contenido. (Error: $_.Exception.Message)"
        $content = "[Error: No se pudo leer el contenido del archivo]"
    }
    
    # Crear el bloque de texto (Here-String)
    $outputBlock = @"
$header
$content

"@ # Una línea en blanco después del contenido para separación

    # Añadir el bloque al archivo de salida
    Add-Content -Path $OutputFullPath -Value $outputBlock -Encoding Utf8
}

Write-Host "---"
Write-Host "¡Exportación completada!" -ForegroundColor Green
Write-Host "Total de archivos procesados: $fileCount"
Write-Host "Archivo de salida guardado en: $OutputFullPath"