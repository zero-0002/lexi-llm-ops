#!/bin/bash
# Legal Retrieval System - Helm Values Update Script
# ===================================================

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

# Configuration
DOCKER_REGISTRY="${DOCKER_REGISTRY:-docker.io}"
DOCKER_NAMESPACE="${DOCKER_NAMESPACE:-legalretrieval}"
IMAGE_TAG="${IMAGE_TAG:-latest}"
HELM_VALUES_DIR="helm/values"
BACKUP_DIR="helm/values/backups"

# Functions
log() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')] ✅${NC} $1"
}

log_error() {
    echo -e "${RED}[$(date +'%Y-%m-%d %H:%M:%S')] ❌${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[$(date +'%Y-%m-%d %H:%M:%S')] ⚠️${NC} $1"
}

log_step() {
    echo -e "${CYAN}[$(date +'%Y-%m-%d %H:%M:%S')] 🚀${NC} $1"
}

# Function to create backup
create_backup() {
    log_step "Creating backup of current values..."
    
    # Create backup directory
    mkdir -p "$BACKUP_DIR"
    
    # Create timestamp for backup
    local timestamp=$(date +%Y%m%d_%H%M%S)
    local backup_subdir="$BACKUP_DIR/backup_$timestamp"
    mkdir -p "$backup_subdir"
    
    # Copy all values files
    if [ -d "$HELM_VALUES_DIR" ]; then
        cp -r "$HELM_VALUES_DIR"/*.yaml "$backup_subdir/" 2>/dev/null || true
        log_success "Backup created: $backup_subdir"
        echo "$backup_subdir" > "$BACKUP_DIR/latest_backup"
    else
        log_warning "Values directory not found: $HELM_VALUES_DIR"
    fi
}

# Function to restore from backup
restore_backup() {
    log_step "Restoring from latest backup..."
    
    if [ -f "$BACKUP_DIR/latest_backup" ]; then
        local latest_backup=$(cat "$BACKUP_DIR/latest_backup")
        
        if [ -d "$latest_backup" ]; then
            cp "$latest_backup"/*.yaml "$HELM_VALUES_DIR/"
            log_success "Restored from backup: $latest_backup"
        else
            log_error "Backup directory not found: $latest_backup"
            return 1
        fi
    else
        log_error "No backup found"
        return 1
    fi
}

# Function to update backend API values
update_backend_values() {
    local backend_file="$HELM_VALUES_DIR/backend-api.yaml"
    
    log_step "Updating backend API values..."
    
    if [ ! -f "$backend_file" ]; then
        log_error "Backend values file not found: $backend_file"
        return 1
    fi
    
    # Create new image configuration
    local new_image_registry="$DOCKER_REGISTRY"
    local new_image_repository="$DOCKER_NAMESPACE/backend"
    local new_image_tag="$IMAGE_TAG"
    
    # Update using yq if available, otherwise use sed
    if command -v yq >/dev/null 2>&1; then
        log "Using yq to update backend values..."
        
        # Update image configuration
        yq eval ".image.registry = \"$new_image_registry\"" -i "$backend_file"
        yq eval ".image.repository = \"$new_image_repository\"" -i "$backend_file"
        yq eval ".image.tag = \"$new_image_tag\"" -i "$backend_file"
        yq eval ".image.pullPolicy = \"Always\"" -i "$backend_file"
        
        log_success "Backend values updated with yq"
    else
        log "Using sed to update backend values..."
        
        # Backup original file
        cp "$backend_file" "$backend_file.bak"
        
        # Update image configuration using sed
        sed -i.tmp "s|registry:.*|registry: \"$new_image_registry\"|g" "$backend_file"
        sed -i.tmp "s|repository:.*|repository: \"$new_image_repository\"|g" "$backend_file"
        sed -i.tmp "s|tag:.*|tag: \"$new_image_tag\"|g" "$backend_file"
        sed -i.tmp "s|pullPolicy:.*|pullPolicy: \"Always\"|g" "$backend_file"
        
        # Clean up temporary files
        rm -f "$backend_file.tmp"
        
        log_success "Backend values updated with sed"
    fi
    
    # Verify changes
    log "Backend image configuration:"
    echo "  Registry: $new_image_registry"
    echo "  Repository: $new_image_repository"
    echo "  Tag: $new_image_tag"
}

# Function to update Celery worker values
update_celery_values() {
    local celery_file="$HELM_VALUES_DIR/celery-worker.yaml"
    
    log_step "Updating Celery worker values..."
    
    if [ ! -f "$celery_file" ]; then
        log_error "Celery values file not found: $celery_file"
        return 1
    fi
    
    # Create new image configuration
    local new_image_registry="$DOCKER_REGISTRY"
    local new_image_repository="$DOCKER_NAMESPACE/backend"  # Same image as backend
    local new_image_tag="$IMAGE_TAG"
    
    # Update using yq if available, otherwise use sed
    if command -v yq >/dev/null 2>&1; then
        log "Using yq to update Celery values..."
        
        # Update image configuration
        yq eval ".image.registry = \"$new_image_registry\"" -i "$celery_file"
        yq eval ".image.repository = \"$new_image_repository\"" -i "$celery_file"
        yq eval ".image.tag = \"$new_image_tag\"" -i "$celery_file"
        yq eval ".image.pullPolicy = \"Always\"" -i "$celery_file"
        
        log_success "Celery values updated with yq"
    else
        log "Using sed to update Celery values..."
        
        # Backup original file
        cp "$celery_file" "$celery_file.bak"
        
        # Update image configuration using sed
        sed -i.tmp "s|registry:.*|registry: \"$new_image_registry\"|g" "$celery_file"
        sed -i.tmp "s|repository:.*|repository: \"$new_image_repository\"|g" "$celery_file"
        sed -i.tmp "s|tag:.*|tag: \"$new_image_tag\"|g" "$celery_file"
        sed -i.tmp "s|pullPolicy:.*|pullPolicy: \"Always\"|g" "$celery_file"
        
        # Clean up temporary files
        rm -f "$celery_file.tmp"
        
        log_success "Celery values updated with sed"
    fi
    
    # Verify changes
    log "Celery image configuration:"
    echo "  Registry: $new_image_registry"
    echo "  Repository: $new_image_repository"
    echo "  Tag: $new_image_tag"
}

# Function to update frontend values
update_frontend_values() {
    local frontend_file="$HELM_VALUES_DIR/frontend.yaml"
    
    log_step "Updating frontend values..."
    
    if [ ! -f "$frontend_file" ]; then
        log_error "Frontend values file not found: $frontend_file"
        return 1
    fi
    
    # Create new image configuration
    local new_image_registry="$DOCKER_REGISTRY"
    local new_image_repository="$DOCKER_NAMESPACE/frontend"
    local new_image_tag="$IMAGE_TAG"
    
    # Update using yq if available, otherwise use sed
    if command -v yq >/dev/null 2>&1; then
        log "Using yq to update frontend values..."
        
        # Update image configuration
        yq eval ".image.registry = \"$new_image_registry\"" -i "$frontend_file"
        yq eval ".image.repository = \"$new_image_repository\"" -i "$frontend_file"
        yq eval ".image.tag = \"$new_image_tag\"" -i "$frontend_file"
        yq eval ".image.pullPolicy = \"Always\"" -i "$frontend_file"
        
        log_success "Frontend values updated with yq"
    else
        log "Using sed to update frontend values..."
        
        # Backup original file
        cp "$frontend_file" "$frontend_file.bak"
        
        # Update image configuration using sed
        sed -i.tmp "s|registry:.*|registry: \"$new_image_registry\"|g" "$frontend_file"
        sed -i.tmp "s|repository:.*|repository: \"$new_image_repository\"|g" "$frontend_file"
        sed -i.tmp "s|tag:.*|tag: \"$new_image_tag\"|g" "$frontend_file"
        sed -i.tmp "s|pullPolicy:.*|pullPolicy: \"Always\"|g" "$frontend_file"
        
        # Clean up temporary files
        rm -f "$frontend_file.tmp"
        
        log_success "Frontend values updated with sed"
    fi
    
    # Verify changes
    log "Frontend image configuration:"
    echo "  Registry: $new_image_registry"
    echo "  Repository: $new_image_repository"
    echo "  Tag: $new_image_tag"
}

# Function to validate updated values
validate_values() {
    log_step "Validating updated values..."
    
    local validation_errors=0
    
    # Check if files exist and are valid YAML
    for file in "backend-api.yaml" "celery-worker.yaml" "frontend.yaml"; do
        local filepath="$HELM_VALUES_DIR/$file"
        
        if [ ! -f "$filepath" ]; then
            log_error "Missing values file: $filepath"
            validation_errors=$((validation_errors + 1))
            continue
        fi
        
        # Check YAML syntax
        if command -v yq >/dev/null 2>&1; then
            if ! yq eval '.' "$filepath" >/dev/null 2>&1; then
                log_error "Invalid YAML syntax in: $filepath"
                validation_errors=$((validation_errors + 1))
            else
                log_success "Valid YAML: $file"
            fi
        else
            log_warning "yq not available, skipping YAML validation for: $file"
        fi
    done
    
    # Check Helm template rendering
    if command -v helm >/dev/null 2>&1; then
        log "Testing Helm template rendering..."
        
        if helm template test-release helm/charts/legal-backend -f "$HELM_VALUES_DIR/backend-api.yaml" >/dev/null 2>&1; then
            log_success "Backend chart templates render successfully"
        else
            log_error "Backend chart template rendering failed"
            validation_errors=$((validation_errors + 1))
        fi
        
        if helm template test-release helm/charts/legal-celery-worker -f "$HELM_VALUES_DIR/celery-worker.yaml" >/dev/null 2>&1; then
            log_success "Celery chart templates render successfully"
        else
            log_error "Celery chart template rendering failed"
            validation_errors=$((validation_errors + 1))
        fi
        
        if helm template test-release helm/charts/legal-frontend -f "$HELM_VALUES_DIR/frontend.yaml" >/dev/null 2>&1; then
            log_success "Frontend chart templates render successfully"
        else
            log_error "Frontend chart template rendering failed"
            validation_errors=$((validation_errors + 1))
        fi
    else
        log_warning "Helm not available, skipping template validation"
    fi
    
    return $validation_errors
}

# Function to show summary
show_summary() {
    log_step "Updated values summary..."
    
    echo -e "\n${CYAN}Updated Image References:${NC}"
    echo "  Backend:     $DOCKER_REGISTRY/$DOCKER_NAMESPACE/backend:$IMAGE_TAG"
    echo "  Celery:      $DOCKER_REGISTRY/$DOCKER_NAMESPACE/backend:$IMAGE_TAG"
    echo "  Frontend:    $DOCKER_REGISTRY/$DOCKER_NAMESPACE/frontend:$IMAGE_TAG"
    
    echo -e "\n${CYAN}Updated Files:${NC}"
    echo "  Backend API: $HELM_VALUES_DIR/backend-api.yaml"
    echo "  Celery:      $HELM_VALUES_DIR/celery-worker.yaml"
    echo "  Frontend:    $HELM_VALUES_DIR/frontend.yaml"
    
    if [ -f "$BACKUP_DIR/latest_backup" ]; then
        local latest_backup=$(cat "$BACKUP_DIR/latest_backup")
        echo -e "\n${CYAN}Backup Location:${NC}"
        echo "  $latest_backup"
        echo -e "\n${CYAN}Restore Command:${NC}"
        echo "  $0 restore"
    fi
}

# Main function
main() {
    echo -e "${GREEN}"
    echo "📝 Legal Retrieval System - Helm Values Update"
    echo "=============================================="
    echo -e "${NC}"
    
    # Load environment if available
    if [ -f ".env" ]; then
        log "Loading environment variables..."
        set -a
        source .env
        set +a
    fi
    
    # Show configuration
    echo -e "${CYAN}Update Configuration:${NC}"
    echo "  Registry: $DOCKER_REGISTRY"
    echo "  Namespace: $DOCKER_NAMESPACE"
    echo "  Tag: $IMAGE_TAG"
    echo "  Values Dir: $HELM_VALUES_DIR"
    echo ""
    
    # Check if values directory exists
    if [ ! -d "$HELM_VALUES_DIR" ]; then
        log_error "Values directory not found: $HELM_VALUES_DIR"
        exit 1
    fi
    
    # Create backup
    create_backup
    
    # Update values
    local update_errors=0
    
    if ! update_backend_values; then
        update_errors=$((update_errors + 1))
    fi
    
    if ! update_celery_values; then
        update_errors=$((update_errors + 1))
    fi
    
    if ! update_frontend_values; then
        update_errors=$((update_errors + 1))
    fi
    
    # Validate changes
    if [ $update_errors -eq 0 ]; then
        if ! validate_values; then
            log_warning "Some validation checks failed"
        fi
    fi
    
    # Show summary
    show_summary
    
    # Final result
    if [ $update_errors -eq 0 ]; then
        echo -e "\n${GREEN}🎉 All Helm values updated successfully!${NC}"
        echo -e "${CYAN}Next steps:${NC}"
        echo "  1. Review changes: git diff $HELM_VALUES_DIR/"
        echo "  2. Deploy updates: ./deploy-pipeline.sh"
        echo "  3. Or test locally: helm template ..."
    else
        echo -e "\n${RED}❌ Update completed with $update_errors error(s)${NC}"
        echo -e "${CYAN}Restore if needed:${NC}"
        echo "  $0 restore"
        exit 1
    fi
}

# Handle arguments
case "${1:-all}" in
    "backend")
        create_backup
        update_backend_values
        validate_values
        ;;
    "celery")
        create_backup
        update_celery_values
        validate_values
        ;;
    "frontend")
        create_backup
        update_frontend_values
        validate_values
        ;;
    "restore")
        restore_backup
        ;;
    "validate")
        validate_values
        ;;
    "all")
        main
        ;;
    *)
        echo "Usage: $0 {backend|celery|frontend|restore|validate|all}"
        echo ""
        echo "Commands:"
        echo "  backend  - Update backend values only"
        echo "  celery   - Update Celery worker values only"
        echo "  frontend - Update frontend values only"
        echo "  restore  - Restore from latest backup"
        echo "  validate - Validate current values"
        echo "  all      - Update all values (default)"
        exit 1
        ;;
esac
