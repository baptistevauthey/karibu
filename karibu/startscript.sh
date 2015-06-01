until './dontrun.sh'; do
    echo "Server 'karibu' crashed with exit code $?.  Respawning.." >&2
    sleep 1
done
