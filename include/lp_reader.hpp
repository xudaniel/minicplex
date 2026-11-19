// minicplex — reader for (a practical subset of) the CPLEX LP file format.
//
// Supported sections: Minimize/Maximize, Subject To, Bounds,
// General(s)/Integer(s), Binary/Binaries, End.  Comments start with '\'.
#pragma once

#include <string>

#include "model.hpp"

namespace mcplex {

Model readLPString(const std::string& text);
Model readLPFile(const std::string& path);

}  // namespace mcplex
